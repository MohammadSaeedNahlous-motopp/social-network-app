from io import BytesIO

import pytest
from PIL import Image
from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.hash import Hash
from models.user import DBUser


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


def test_register_user(client):
    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        },
    )

    print(response.json())

    assert response.status_code == 201


def test_register_duplicate_email(client):
    user = {"name": "John Doe", "email": "john@example.com", "password": "password123"}

    client.post("/auth/register", data=user)

    response = client.post("/auth/register", data=user)

    assert response.status_code == 400


def test_register_missing_email(client):
    response = client.post(
        "/auth/register", data={"name": "John Doe", "password": "password123"}
    )

    assert response.status_code == 422


def test_register_password_is_hashed(client, db: Session):
    response = client.post(
        "/auth/register",
        data={
            "name": "John Deeeoe",
            "email": "jddwqddeeeehn@example.com",
            "password": "password123",
        },
    )

    print(response.json())
    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == "jddwqddeeeehn@example.com").first()

    assert user is not None
    assert user.password != "password123"
    assert Hash.verify(user.password, "password123")


def test_register_without_optional_fields(client):
    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "jwwwdd434343hn@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201


@pytest.mark.parametrize("gender", ["male", "female", "other", "prefer_not_to_say"])
def test_register_with_valid_gender(client, db: Session, gender):
    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": f"{gender}_test@example.com",
            "password": "password123",
            "gender": gender,
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == f"{gender}_test@example.com").first()

    assert user is not None
    assert user.gender.value == gender


def test_login_success(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="login1_test@example.com",
        password=Hash.hash("password123"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        "/auth/login",
        data={"username": "login1_test@example.com", "password": "password123"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == user.id


def test_login_wrong_password(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="wrong_password@example.com",
        password=Hash.hash("password123"),
    )

    db.add(user)
    db.commit()

    response = client.post(
        "/auth/login",
        data={"username": "wrong_password@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_user_not_found(client):
    response = client.post(
        "/auth/login",
        data={"username": "does_not_exist@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_missing_password(client):
    response = client.post("/auth/login", data={"username": "login_test@example.com"})

    assert response.status_code == 422


def test_login_missing_username(client):
    response = client.post("/auth/login", data={"password": "password123"})

    assert response.status_code == 422


def test_create_user_with_profile_image(client, db: Session):
    image = create_test_image()

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "create_image@example.com",
            "password": "password123",
            "bio": "Test bio",
            "phone": "0612345678",
            "location": "Rotterdam",
            "gender": "male",
        },
        files={"profile_img": ("profile.jpg", image, "image/jpeg")},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "John Doe"
    assert data["email"] == "create_image@example.com"
    assert data["profile_img"] is not None

    user = db.query(DBUser).filter(DBUser.email == "create_image@example.com").first()

    assert user is not None
    assert user.profile_img is not None


def test_create_user_without_profile_image(client, db: Session):
    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "no_imaeeeeeege@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == "no_imaeeeeeege@example.com").first()

    assert user is not None
    assert user.profile_img is None


def test_create_user_with_existing_email(client, db: Session):
    existing_user = DBUser(
        name="Existing User",
        email="existing@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(existing_user)
    db.commit()

    image = create_test_image()

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": "existing@example.com",
            "password": "password123",
        },
        files={"profile_img": ("profile.jpg", image, "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
