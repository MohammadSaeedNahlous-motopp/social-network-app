from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import status



def test_update_group_deletes_old_background_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    db: Session,
    tmp_path,
):
    # Arrange
    user = authenticated_user(email="background_replace@example.com")

    old_background = tmp_path / "old_background.jpg"
    old_background.write_bytes(b"old background")

    new_background = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img="profile.jpg",
        background_img=str(old_background),
        is_public=True,
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

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Original Name"
    assert data["description"] == "Original description"
    assert data["is_public"] is True

    assert data["background_img"] != original_background_img
    assert Path(data["background_img"]).exists()

    assert not old_background.exists()

    db.refresh(test_group)

    assert test_group.background_img != original_background_img
    assert Path(test_group.background_img).exists()


def test_update_group_deletes_old_profile_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    db: Session,
    tmp_path,
):
    # Arrange
    user = authenticated_user(email="profile_replace@example.com")

    old_profile = tmp_path / "old_profile.jpg"
    old_profile.write_bytes(b"old profile")

    new_profile = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img=str(old_profile),
        background_img="background.jpg",
        is_public=True,
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

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Original Name"
    assert data["description"] == "Original description"
    assert data["is_public"] is True

    assert data["profile_img"] != original_profile_img
    assert Path(data["profile_img"]).exists()

    assert not old_profile.exists()

    db.refresh(test_group)

    assert test_group.profile_img != original_profile_img
    assert Path(test_group.profile_img).exists()


def test_update_group_background_image_does_not_delete_profile_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
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


def test_update_group_profile_image_does_not_delete_background_image(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    db: Session,
    tmp_path,
):
    # Arrange
    user = authenticated_user(email="profile_only@example.com")

    old_background = tmp_path / "old_background.jpg"
    old_profile = tmp_path / "old_profile.jpg"

    old_background.write_bytes(b"old background")
    old_profile.write_bytes(b"old profile")

    new_profile = generate_test_image()

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img=str(old_profile),
        background_img=str(old_background),
        is_public=True,
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

    # Assert
    assert response.status_code == status.HTTP_200_OK

    db.refresh(test_group)

    assert old_profile.exists() is False
    assert old_background.exists() is True

    assert test_group.profile_img != str(old_profile)
    assert test_group.background_img == str(old_background)

    assert Path(test_group.profile_img).exists()


def test_update_group_image_only_preserves_other_fields(
    client,
    authenticated_user,
    create_test_group,
    generate_test_image,
    db: Session,
):
    # Arrange
    user = authenticated_user(email="image_only@example.com")

    test_group = create_test_group(
        owner=user,
        name="Original Name",
        description="Original description",
        profile_img="profile.jpg",
        background_img="background.jpg",
        is_public=True,
    )

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

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Original Name"
    assert data["description"] == "Original description"
    assert data["profile_img"] == "profile.jpg"
    assert data["is_public"] is True
    assert data["background_img"] != "background.jpg"
    assert Path(data["background_img"]).exists()

    db.refresh(test_group)

    assert test_group.name == "Original Name"
    assert test_group.description == "Original description"
    assert test_group.profile_img == "profile.jpg"
    assert test_group.is_public is True
    assert test_group.background_img != "background.jpg"
