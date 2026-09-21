from pathlib import Path

import pytest
from sqlalchemy.orm import Session
from fastapi import status
from fastapi.responses import FileResponse

from models.enums import GroupRole, ImageType
from service.image import save_image


@pytest.mark.asyncio
async def test_update_group_deletes_old_background_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    create_test_group_member,
    get_test_group_role,
    db: Session,
    get_response_filename,
):
    # Arrange
    image = generate_test_image()
    upload_image = image.as_upload_file()
    upload_image.filename = "old_background.jpg"

    image_path = await save_image(
        file=upload_image, image_type=ImageType.group_background_picture
    )
    image_path: Path = Path(image_path)
    save_dir = image_path.parent

    user = authenticated_user(email="background_replace@example.com")

    old_background = image_path

    new_background = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img="profile.jpg",
        background_img=str(old_background),
        is_public=True,
    )
    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )

    original_background_img = test_group.background_img

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={},
        files={
            "group_background_img": (
                "new_background.jpg",
                new_background,
                "image/jpeg",
            )
        },
    )

    image_response: FileResponse = client.get(
        f"/images/group/{test_group.id}/background"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert image_response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Original Name"
    assert data["description"] == "Original description"
    assert data["is_public"] is True

    assert get_response_filename(image_response) != Path(original_background_img).name
    assert Path(save_dir, get_response_filename(image_response)).exists()

    assert not old_background.exists()

    db.refresh(test_group)

    assert test_group.background_img != original_background_img
    assert Path(test_group.background_img).exists()


@pytest.mark.asyncio
async def test_update_group_deletes_old_profile_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    create_test_group_member,
    get_test_group_role,
    db: Session,
    get_response_filename,
):
    # Arrange
    image = generate_test_image()
    upload_image = image.as_upload_file()
    upload_image.filename = "old_profile.jpg"

    image_path = await save_image(file=upload_image, image_type=ImageType.group_picture)
    image_path: Path = Path(image_path)
    save_dir = image_path.parent

    user = authenticated_user(email="profile_replace@example.com")

    old_profile = image_path
    new_profile = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img=str(old_profile),
        background_img="background.jpg",
        is_public=True,
    )
    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )

    original_profile_img = test_group.profile_img

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={},
        files={
            "group_img": (
                "new_profile.jpg",
                new_profile,
                "image/jpeg",
            )
        },
    )
    image_response: FileResponse = client.get(f"/images/group/{test_group.id}/icon")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert image_response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Original Name"
    assert data["description"] == "Original description"
    assert data["is_public"] is True

    assert get_response_filename(image_response) != Path(original_profile_img).name
    assert Path(save_dir, get_response_filename(image_response)).exists()

    assert not old_profile.exists()

    db.refresh(test_group)

    assert test_group.profile_img != original_profile_img
    assert Path(test_group.profile_img).exists()


def test_update_group_background_image_does_not_delete_profile_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    create_test_group_member,
    get_test_group_role,
    db: Session,
    tmp_path,
):
    # Arrange
    user = authenticated_user(email="background_only@example.com")

    old_background = tmp_path / "old_background.jpg"
    old_profile = tmp_path / "old_profile.jpg"

    old_background.write_bytes(b"old background")
    old_profile.write_bytes(b"old profile")

    new_background = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img=str(old_profile),
        background_img=str(old_background),
        is_public=True,
    )
    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={},
        files={
            "group_background_img": (
                "new_background.jpg",
                new_background,
                "image/jpeg",
            )
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    db.refresh(test_group)

    assert not old_background.exists()
    assert old_profile.exists()

    assert test_group.background_img != str(old_background)
    assert test_group.profile_img == str(old_profile)

    assert Path(test_group.background_img).exists()


@pytest.mark.asyncio
async def test_update_group_profile_image_does_not_delete_background_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    create_test_group_member,
    get_test_group_role,
    db: Session,
    get_response_filename,
):
    # Arrange
    image = generate_test_image()
    upload_image = image.as_upload_file()
    upload_image.filename = "old_profile.jpg"

    image_path = await save_image(
        file=upload_image, image_type=ImageType.group_background_picture
    )
    image_path: Path = Path(image_path)

    user = authenticated_user(email="profile_only@example.com")

    old_background = image_path

    image_path = Path(
        await save_image(file=upload_image, image_type=ImageType.group_picture)
    )

    old_profile = image_path

    new_profile = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img=str(old_profile),
        background_img=str(old_background),
        is_public=True,
    )
    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={},
        files={
            "group_img": (
                "new_profile.jpg",
                new_profile,
                "image/jpeg",
            )
        },
    )
    profile_response: FileResponse = client.get(f"/images/group/{test_group.id}/icon")
    background_response: FileResponse = client.get(
        f"/images/group/{test_group.id}/background"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert profile_response.status_code == status.HTTP_200_OK
    assert background_response.status_code == status.HTTP_200_OK

    db.refresh(test_group)

    assert old_profile.exists() is False
    assert old_background.exists() is True

    assert test_group.profile_img != str(old_profile)
    assert test_group.background_img == str(old_background)

    assert Path(test_group.profile_img).exists()


@pytest.mark.asyncio
async def test_update_group_image_only_preserves_other_fields(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    create_test_group_member,
    get_test_group_role,
    db: Session,
    get_response_filename,
):
    # Arrange
    image = generate_test_image()
    upload_image = image.as_upload_file()
    upload_image.filename = "old_background.jpg"

    image_path = await save_image(
        file=upload_image, image_type=ImageType.group_background_picture
    )
    image_path: Path = Path(image_path)
    save_dir = image_path.parent

    user = authenticated_user(email="image_only@example.com")

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img="profile.jpg",
        background_img=str(image_path),
        is_public=True,
    )
    create_test_group_member(
        user=user, group=test_group, role=get_test_group_role(GroupRole.administrator)
    )
    original_background = test_group.background_img
    new_background = generate_test_image()

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        data={},
        files={
            "group_background_img": (
                "new_background.jpg",
                new_background,
                "image/jpeg",
            )
        },
    )

    image_response: FileResponse = client.get(
        f"/images/group/{test_group.id}/background"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert image_response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Original Name"
    assert data["description"] == "Original description"
    assert data["is_public"] is True

    assert Path(save_dir, get_response_filename(image_response)).exists()

    db.refresh(test_group)

    assert test_group.name == "Original Name"
    assert test_group.description == "Original description"
    assert test_group.is_public is True
    assert test_group.background_img != original_background
