import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.hash import Hash
from models.user import DBUser


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "john@example.com"
    assert response.json()["name"] == "John Doe"


def test_register_duplicate_email(client):
    user = {"name": "John Doe", "email": "john@example.com", "password": "password123"}

    client.post("/auth/register", json=user)

    response = client.post("/auth/register", json=user)

    assert response.status_code == 400


def test_register_missing_email(client):
    response = client.post(
        "/auth/register", json={"name": "John Doe", "password": "password123"}
    )

    assert response.status_code == 422


def test_register_password_is_hashed(client, db: Session):
    response = client.post(
        "/auth/register",
        json={
            "name": "John Doe",
            "email": "jo33333ddddhn@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    user = db.query(DBUser).filter(DBUser.email == "jo33333hn@example.com").first()

    assert user is not None
    assert user.password != "password123"
    assert Hash.verify(user.password, "password123")


def test_register_without_optional_fields(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "John Doe",
            "email": "jowwww434343hn@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200




@pytest.mark.parametrize("gender", [
    "male",
    "female",
    "other",
    "prefer_not_to_say"
])
def test_register_with_valid_gender(client, db: Session, gender):
    response = client.post(
        "/auth/register",
        json={
            "name": "John Doe",
            "email": f"{gender}_test@example.com",
            "password": "password123",
            "gender": gender
        }
    )

    assert response.status_code == 200

    user = db.query(DBUser).filter(
        DBUser.email == f"{gender}_test@example.com"
    ).first()

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
        data={
            "username": "login1_test@example.com",
            "password": "password123"
        },
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
