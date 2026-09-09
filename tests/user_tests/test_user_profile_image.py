from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


# ============================================================
# PROFILE IMAGE TESTS
# ============================================================


def test_edit_user_profile_image(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="profile_image_original@example.com",
        name="Profile Image User",
    )

    image = create_test_image()

    response = client.put(
        "/users/edit",
        data={
            "bio": "Updated bio",
        },
        files={
            "profile_img": (
                "new_profile.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["bio"] == "Updated bio"
    assert data["profile_img"] is not None

    db.refresh(user)

    assert user.bio == "Updated bio"
    assert user.profile_img is not None


def test_edit_user_remove_profile_image(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="remove_profile_image@example.com",
        name="Remove Image User",
    )

    # First upload a REAL profile image
    image = create_test_image()

    response = client.put(
        "/users/edit",
        files={
            "profile_img": (
                "profile.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    db.refresh(user)

    assert user.profile_img is not None

    # Now remove the profile image
    response = client.put(
        "/users/edit",
        data={
            "remove_profile_img": "true",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["profile_img"] is None

    db.refresh(user)

    assert user.profile_img is None
