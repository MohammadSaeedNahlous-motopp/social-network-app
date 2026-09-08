import pytest
from sqlalchemy.orm import Session


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
def test_update_group(
    client,
    authenticated_user,
    create_test_group,
    db: Session,
    update_data,
    expected_data,
):
    # Arrange
    user = authenticated_user(email="update_test@example.com")

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img="profile.jpg",
        background_img="background.jpg",
        is_public=True,
    )

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        json=update_data,
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["name"] == expected_data["name"]
    assert data["description"] == expected_data["description"]
    assert data["is_public"] is expected_data["is_public"]
    assert data["background_img"] == expected_data["background_img"]
    assert data["profile_img"] == expected_data["profile_img"]

    db.refresh(test_group)

    assert test_group.name == expected_data["name"]
    assert test_group.description == expected_data["description"]
    assert test_group.is_public is expected_data["is_public"]
    assert test_group.background_img == expected_data["background_img"]
    assert test_group.profile_img == expected_data["profile_img"]


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
        json={"name": "Hacked Name"},
    )

    # Assert
    assert response.status_code == 403
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
        json={"name": "New Name"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_update_group_empty_request(
    client,
    authenticated_user,
    create_test_group,
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

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        json={},
    )

    # Assert
    assert response.status_code == 400
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

    original_updated_at = test_group.updated_at
    new_group_name = "New Name"

    # Act
    response = client.put(
        f"/groups/edit/{test_group.id}",
        json={"name": new_group_name},
    )

    # Assert
    assert response.status_code == 200

    db.refresh(test_group)

    assert test_group.name == new_group_name
    assert test_group.updated_at is not None
    assert test_group.updated_at > original_updated_at
