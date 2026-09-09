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
# VALID IMAGE TESTS
# ============================================================


def test_create_user_with_png_image(client, db: Session):
    email = unique_email("png_image")

    image = create_test_image("PNG")

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
                "profile.png",
                image,
                "image/png",
            )
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None
    assert user.profile_img is not None


def test_create_user_with_webp_image(client, db: Session):
    email = unique_email("webp_image")

    image = create_test_image("WEBP")

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
                "profile.webp",
                image,
                "image/webp",
            )
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None
    assert user.profile_img is not None
