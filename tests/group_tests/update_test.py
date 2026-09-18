from pathlib import Path

import pytest

from fastapi import status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from models.enums import GroupRole, ImageType
from service.image import save_image


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_data",
    [
        (
            {"name": "New Name"},
            {
                "name": "New Name",
                "description": "Original description",
                "background_img": "background.jpg",
                "profile_img": "profile.jpg",
                "is_public": True,
            },
        ),
        (
            {"description": "New description"},
            {
                "name": "Original Name",
                "description": "New description",
                "background_img": "background.jpg",
                "profile_img": "profile.jpg",
                "is_public": True,
            },
        ),
        (
            {"background_img": "new_background.jpg"},
            {
                "name": "Original Name",
                "description": "Original description",
                "background_img": "new_background.jpg",
                "profile_img": "profile.jpg",
                "is_public": True,
            },
        ),
        (
            {"profile_img": "new_profile.jpg"},
            {
                "name": "Original Name",
                "description": "Original description",
                "background_img": "background.jpg",
                "profile_img": "new_profile.jpg",
                "is_public": True,
            },
        ),
        (
            {"is_public": False},
            {
                "name": "Original Name",
                "description": "Original description",
                "background_img": "background.jpg",
                "profile_img": "profile.jpg",
                "is_public": False,
            },
        ),
        (
            {
                "name": "New Name",
                "description": "New description",
                "background_img": "new_background.jpg",
                "profile_img": "new_profile.jpg",
                "is_public": False,
            },
            {
                "name": "New Name",
                "description": "New description",
                "background_img": "new_background.jpg",
                "profile_img": "new_profile.jpg",
                "is_public": False,
            },
        ),
    ],
)
async def test_update_group(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    generate_test_image,
    db: Session,
    update_data,
    expected_data,
    get_response_filename
):
    # Arrange
    user = authenticated_user(email="update_test@example.com")

    group_image = generate_test_image()
    group_background_image = generate_test_image()

    initial_group_image = group_image.as_upload_file()
    initial_group_background_image = group_background_image.as_upload_file()

    initial_group_image.filename = await save_image(
        file=initial_group_image,
        image_type=ImageType.group_picture,
    )

    initial_group_background_image.filename = await save_image(
        file=initial_group_background_image,
        image_type=ImageType.group_background_picture,
    )

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img=initial_group_image.filename,
        background_img=initial_group_background_image.filename,
        is_public=True,
    )

    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )


    original_background_img = Path(test_group.background_img).name
    original_profile_img = Path(test_group.profile_img).name

    # Act
    files = {}
    form_data = update_data.copy()

    if form_data.get("profile_img", " ").startswith("new"):
        files["group_img"] = (form_data.pop("profile_img"), group_image, "image/jpeg")

    if form_data.get("background_img", " ").startswith("new"):
        files["group_background_img"] = (
            form_data.pop("background_img"),
            group_background_image,
            "image/jpeg",
        )
    response = client.put(f"/groups/edit/{test_group.id}", data=form_data, files=files)

    icon_image_response: FileResponse = client.get(f"/images/group/{test_group.id}/icon")
    background_image_response: FileResponse = client.get(f"/images/group/{test_group.id}/background")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == expected_data["name"]
    assert data["description"] == expected_data["description"]
    assert data["is_public"] is expected_data["is_public"]

    filename = get_response_filename(icon_image_response)
    if "profile_img" in update_data:
        assert icon_image_response.status_code == status.HTTP_200_OK
        assert filename != original_profile_img
    else:
        assert filename == original_profile_img

    filename = get_response_filename(background_image_response)
    if "background_img" in update_data:
        assert background_image_response.status_code == status.HTTP_200_OK
        assert filename != original_background_img
    else:
        assert filename == original_background_img

    db.refresh(test_group)

    assert test_group.name == expected_data["name"]
    assert test_group.description == expected_data["description"]
    assert test_group.is_public is expected_data["is_public"]

    filename = get_response_filename(background_image_response)
    if "background_img" in update_data:
        assert Path(test_group.background_img).name != original_background_img
    else:
        assert filename == original_background_img

    filename = get_response_filename(icon_image_response)
    if "profile_img" in update_data:
        assert Path(test_group.profile_img).name != original_profile_img
    else:
        assert filename == original_profile_img


def test_update_group_forbidden(
    client,
    create_test_user,
    create_test_group,
    authenticated_user,
    db: Session,
):
    # Arrange
    owner = create_test_user(email="group_owner@example.com")
    authenticated_user(email="other_user@example.com")

    test_group = create_test_group(
        owner=owner,
        name="Original Name",
        description="Original description",
        is_public=True,
    )

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={"name": "Hacked Name"},
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == ("User has no permission to edit group")

    db.refresh(test_group)

    assert test_group.name == "Original Name"


def test_update_group_not_found(
    client,
    authenticated_user,
):
    # Arrange
    authenticated_user(email="update_not_found@example.com")

    # Act
    response = client.put(
        "/groups/edit/999999",
        data={"name": "New Name"},
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"


def test_update_group_empty_request(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db: Session,
):
    # Arrange
    user = authenticated_user(email="empty_update@example.com")

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        is_public=True,
    )

    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={},
    )
    print(response.json())
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == (
        "At least one field must be provided for update"
    )

    db.refresh(test_group)

    assert test_group.name == "Original Name"
    assert test_group.description == "Original description"
    assert test_group.is_public is True


def test_update_group_updates_updated_at(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db: Session,
):
    # Arrange
    user = authenticated_user(email="updated_at_test@example.com")

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        is_public=True,
    )

    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )

    original_updated_at = test_group.updated_at
    new_group_name = "New Name"

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={"name": new_group_name},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    db.refresh(test_group)

    assert test_group.name == new_group_name
    assert test_group.updated_at is not None
    assert test_group.updated_at > original_updated_at
