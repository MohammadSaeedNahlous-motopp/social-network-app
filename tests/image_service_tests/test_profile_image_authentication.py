from io import BytesIO

from PIL import Image
from fastapi import status


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


def test_edit_user_profile_image_unauthorized(client):
    image = create_test_image()

    response = client.put(
        "/users/edit",
        data={
            "name": "John Doe",
            "email": "unauthorized@example.com",
        },
        files={
            "profile_img": (
                "profile.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
