from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session

from models.user import DBUser


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


def test_create_user_with_invalid_image_type(client):
    fake_file = BytesIO(b"This is not an image")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "invalid_image@example.com",
            "password": "password123",
        },
        files={"profile_img": ("profile.txt", fake_file, "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only JPG, PNG, and WEBP images are allowed."


def test_create_user_with_fake_image(client):
    fake_file = BytesIO(b"This is not really an image")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "fake_image@example.com",
            "password": "password123",
        },
        files={"profile_img": ("profile.jpg", fake_file, "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file."


def test_create_user_with_png_image(client, db: Session):
    image = create_test_image("PNG")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "png_imaagaae1@example.com",
            "password": "password123",
        },
        files={"profile_img": ("profile.png", image, "image/png")},
    )

    print(response.json())
    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == "png_imaagaae1@example.com").first()

    assert user is not None
    assert user.profile_img is not None


def test_create_user_with_webp_image(client, db: Session):
    image = create_test_image("WEBP")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "webp_imwage@example.com",
            "password": "password123",
        },
        files={"profile_img": ("profile.webp", image, "image/webp")},
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == "webp_image@example.com").first()

    assert user is not None
    assert user.profile_img is not None


def test_create_user_with_image_too_large(client):
    # Create a fake file larger than 5 MB
    large_file = BytesIO(b"x" * (5 * 1024 * 1024 + 1))

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "large_image@example.com",
            "password": "password123",
        },
        files={"profile_img": ("large.jpg", large_file, "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Profile image must be smaller than 5 MB."


def test_edit_user_profile_image_unauthorized(client):
    image = create_test_image()

    response = client.put(
        "/users/edit",
        data={"name": "John Doe", "email": "unauthorized@example.com"},
        files={"profile_img": ("profile.jpg", image, "image/jpeg")},
    )

    assert response.status_code == 401
