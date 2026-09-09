from io import BytesIO
from uuid import uuid4

from PIL import Image
from sqlalchemy.orm import Session

from models.user import DBUser


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


def unique_email(prefix="test"):
    return f"{prefix}_{uuid4().hex}@example.com"


# ============================================================
# INVALID IMAGE TESTS
# ============================================================


def test_create_user_with_invalid_image_type(client):
    email = unique_email("invalid_image")

    fake_file = BytesIO(b"This is not an image")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
        files={
            "profile_img": (
                "profile.txt",
                fake_file,
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Only JPG, PNG, and WEBP images are allowed.")


def test_create_user_with_fake_image(client):
    email = unique_email("fake_image")

    fake_file = BytesIO(b"This is not really an image")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
        files={
            "profile_img": (
                "profile.jpg",
                fake_file,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file."


def test_create_user_with_image_too_large(client):
    email = unique_email("large_image")

    # Fake file larger than 5 MB
    large_file = BytesIO(b"x" * (5 * 1024 * 1024 + 1))

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
        files={
            "profile_img": (
                "large.jpg",
                large_file,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Image must be smaller than 5 MB.")
