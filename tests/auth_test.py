from io import BytesIO
from uuid import uuid4

import pytest
from PIL import Image
from sqlalchemy.orm import Session

from db.hash import Hash
from models.user import DBUser


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


def unique_email(prefix="test"):
    return f"{prefix}_{uuid4().hex}@example.com"


# =========================
# REGISTER TESTS
# =========================


def test_register_user(client):
    email = unique_email("register_user")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
    )

    assert response.status_code == 201


def test_create_user_with_profile_image(client, db: Session):
    email = unique_email("create_image")
    image = create_test_image()

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
            "bio": "Test bio",
            "phone": "0612345678",
            "location": "Rotterdam",
            "gender": "male",
        },
        files={
            "profile_img": (
                "profile.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None
    assert user.profile_img is not None
    assert user.bio == "Test bio"
    assert user.phone == "0612345678"
    assert user.location == "Rotterdam"

    # Works whether gender is stored as an enum or string
    assert (
        str(user.gender.value if hasattr(user.gender, "value") else user.gender)
        == "male"
    )


def test_create_user_without_profile_image(client, db: Session):
    email = unique_email("without_image")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None
    assert user.profile_img is None


def test_create_user_with_existing_email(client, db: Session):
    email = unique_email("existing_user")

    existing_user = DBUser(
        name="Existing User",
        email=email,
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
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
        files={
            "profile_img": (
                "profile.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_password_is_hashed(client, db: Session):
    email = unique_email("hashed_password")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None
    assert user.password != "password123"
    assert Hash.verify(user.password, "password123")


def test_register_without_optional_fields(client):
    email = unique_email("without_optional_fields")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
        },
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "gender",
    [
        "male",
        "female",
        "other",
        "prefer_not_to_say",
    ],
)
def test_register_with_valid_gender(client, db: Session, gender):
    email = unique_email(f"{gender}_registration")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
            "gender": gender,
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None

    stored_gender = user.gender.value if hasattr(user.gender, "value") else user.gender

    assert stored_gender == gender


def test_register_with_all_optional_fields(client, db: Session):
    email = unique_email("full_registration")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "password123",
            "bio": "Hello, this is my bio",
            "phone": "0612345678",
            "location": "Rotterdam",
            "gender": "male",
        },
    )

    assert response.status_code == 201

    user = db.query(DBUser).filter(DBUser.email == email).first()

    assert user is not None
    assert user.name == "John Doe"
    assert user.bio == "Hello, this is my bio"
    assert user.phone == "0612345678"
    assert user.location == "Rotterdam"

    stored_gender = user.gender.value if hasattr(user.gender, "value") else user.gender

    assert stored_gender == "male"


def test_register_passwords_do_not_match(client):
    email = unique_email("password_mismatch")

    response = client.post(
        "/auth/register",
        data={
            "name": "John Doe",
            "email": email,
            "password": "password123",
            "repeat_password": "differentpassword",
        },
    )

    assert response.status_code == 400


# =========================
# LOGIN TESTS
# =========================


def test_login_success(client, db: Session):
    email = unique_email("login_success")

    user = DBUser(
        name="John Doe",
        email=email,
        password=Hash.hash("password123"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == user.id


def test_login_wrong_password(client, db: Session):
    email = unique_email("wrong_password")

    user = DBUser(
        name="John Doe",
        email=email,
        password=Hash.hash("password123"),
    )

    db.add(user)
    db.commit()

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_user_not_found(client):
    email = unique_email("does_not_exist")

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_missing_password(client):
    response = client.post(
        "/auth/login",
        data={
            "username": unique_email("login_test"),
        },
    )

    assert response.status_code == 422


def test_login_missing_username(client):
    response = client.post(
        "/auth/login",
        data={
            "password": "password123",
        },
    )

    assert response.status_code == 422
