from pathlib import Path

import pytest

from sqlalchemy.orm import Session
from fastapi.responses import FileResponse


# ============================================================
# PROFILE IMAGE TESTS
# ============================================================


@pytest.mark.asyncio
async def test_edit_user_profile_image(
    client, db: Session, authenticated_user, generate_test_image, get_response_filename
):
    user = authenticated_user(
        email="profile_image_original@example.com",
        name="Profile Image User",
    )

    image = generate_test_image()

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
    image_response: FileResponse = client.get(f"/images/profile/{user.id}")

    assert response.status_code == 200
    assert image_response.status_code == 200

    data = response.json()

    assert data["bio"] == "Updated bio"

    db.refresh(user)

    assert user.bio == "Updated bio"
    assert Path(user.profile_img).name == get_response_filename(image_response)


def test_edit_user_remove_profile_image(
    client, db: Session, authenticated_user, generate_test_image, get_response_filename
):
    user = authenticated_user(
        email="remove_profile_image@example.com",
        name="Remove Image User",
    )

    # First upload a REAL profile image
    image = generate_test_image()

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

    image_response: FileResponse = client.get(f"/images/profile/{user.id}")

    assert response.status_code == 200
    assert image_response.status_code == 200

    db.refresh(user)

    assert Path(user.profile_img).exists()

    # Now remove the profile image
    old_img_path = Path(user.profile_img)
    response = client.put(
        "/users/edit",
        data={
            "remove_profile_img": "true",
        },
    )

    assert response.status_code == 200

    db.refresh(user)

    assert user.profile_img is None
    assert not Path(old_img_path).exists()
