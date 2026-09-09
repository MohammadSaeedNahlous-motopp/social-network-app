from uuid import uuid4

from fastapi import status


def unique_email(prefix="test"):
    return f"{prefix}_{uuid4().hex}@example.com"


# ============================================================
# LOGIN TESTS
# ============================================================


def test_login_success(client, create_test_user):
    email = unique_email("login_success")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == user.id


def test_login_wrong_password(client, create_test_user):
    email = unique_email("wrong_password")

    create_test_user(
        email=email,
        name="John Doe",
    )

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json()["detail"] == ("Incorrect email or password")


def test_login_user_not_found(client):
    email = unique_email("does_not_exist")

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json()["detail"] == ("Incorrect email or password")


def test_login_missing_password(client):
    response = client.post(
        "/auth/login",
        data={
            "username": unique_email("login_test"),
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_login_missing_username(client):
    response = client.post(
        "/auth/login",
        data={
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
