from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from db.session import hash_token, get_session_by_token
from models.session import DBSession


def unique_email(prefix="test"):
    return f"{prefix}_{uuid4().hex}@example.com"


# ============================================================
# SESSION CREATION / LOGIN TESTS
# ============================================================


def test_login_creates_session(client, db, create_test_user):
    email = unique_email("session_login")

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

    assert "session_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    stored_session = db.query(DBSession).filter(DBSession.user_id == user.id).first()

    assert stored_session is not None

    assert stored_session.session_hash == hash_token(data["session_token"])

    assert stored_session.refresh_hash == hash_token(data["refresh_token"])

    assert stored_session.revoked_at is None


def test_login_creates_unique_sessions(
    client,
    db,
    create_test_user,
):
    email = unique_email("multiple_sessions")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    first_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    second_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert first_response.status_code == status.HTTP_200_OK
    assert second_response.status_code == status.HTTP_200_OK

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["session_token"] != second_data["session_token"]
    assert first_data["refresh_token"] != second_data["refresh_token"]

    sessions = db.query(DBSession).filter(DBSession.user_id == user.id).all()

    assert len(sessions) == 2


# ============================================================
# SESSION AUTHENTICATION TESTS
# ============================================================


def test_invalid_session_token_is_rejected(db):
    with pytest.raises(HTTPException) as exc_info:
        get_session_by_token(
            "invalid_session_token",
            db,
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


# ============================================================
# REFRESH TESTS
# ============================================================


def test_refresh_session_token(
    client,
    db,
    create_test_user,
):
    email = unique_email("refresh")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    login_data = login_response.json()

    old_session_token = login_data["session_token"]
    refresh_token = login_data["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["session_token"] != old_session_token
    assert data["refresh_token"] == refresh_token
    assert data["token_type"] == "bearer"

    stored_session = db.query(DBSession).filter(DBSession.user_id == user.id).first()

    assert stored_session is not None

    assert stored_session.session_hash == hash_token(data["session_token"])

    assert stored_session.refresh_hash == hash_token(refresh_token)


def test_old_session_token_is_invalid_after_refresh(
    client,
    create_test_user,
    db,
):
    email = unique_email("old_token")

    create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    data = login_response.json()

    old_session_token = data["session_token"]
    refresh_token = data["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == status.HTTP_200_OK

    new_session_token = refresh_response.json()["session_token"]

    # Old token should no longer resolve.
    with pytest.raises(HTTPException) as exc_info:
        get_session_by_token(
            old_session_token,
            db,
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    # New token should resolve successfully.
    new_session = get_session_by_token(
        new_session_token,
        db,
    )

    assert new_session is not None


def test_refresh_with_invalid_token(client):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid_refresh_token",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_refresh_token_is_not_rotated(
    client,
    create_test_user,
):
    email = unique_email("refresh_reuse")

    create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    refresh_token = login_response.json()["refresh_token"]

    first_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    second_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert first_refresh.status_code == status.HTTP_200_OK
    assert second_refresh.status_code == status.HTTP_200_OK

    assert first_refresh.json()["refresh_token"] == refresh_token

    assert second_refresh.json()["refresh_token"] == refresh_token


# ============================================================
# LOGOUT TESTS
# ============================================================


def test_logout_revokes_current_session(
    client,
    db,
    create_test_user,
):
    email = unique_email("logout")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    session_token = login_response.json()["session_token"]

    response = client.patch(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {session_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == ("Logged out successfully.")

    stored_session = db.query(DBSession).filter(DBSession.user_id == user.id).first()

    assert stored_session is not None
    assert stored_session.revoked_at is not None


def test_revoked_session_cannot_authenticate(
    client,
    db,
    create_test_user,
):
    email = unique_email("revoked_session")

    create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    session_token = login_response.json()["session_token"]

    logout_response = client.patch(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {session_token}",
        },
    )

    assert logout_response.status_code == status.HTTP_200_OK

    with pytest.raises(HTTPException) as exc_info:
        get_session_by_token(
            session_token,
            db,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    assert exc_info.value.detail == ("Session has been revoked")


def test_logout_only_revokes_current_session(
    client,
    db,
    create_test_user,
):
    email = unique_email("logout_one_session")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    first_login = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    second_login = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert first_login.status_code == status.HTTP_200_OK
    assert second_login.status_code == status.HTTP_200_OK

    first_token = first_login.json()["session_token"]
    second_token = second_login.json()["session_token"]

    logout_response = client.patch(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    assert logout_response.status_code == status.HTTP_200_OK

    # First session must be revoked.
    with pytest.raises(HTTPException) as exc_info:
        get_session_by_token(
            first_token,
            db,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    # Second session must still be valid.
    second_session = get_session_by_token(
        second_token,
        db,
    )

    assert second_session is not None
    assert second_session.user_id == user.id


# ============================================================
# LOGOUT ALL TESTS
# ============================================================


def test_logout_all_revokes_all_sessions(
    client,
    db,
    create_test_user,
):
    email = unique_email("logout_all")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    first_login = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    second_login = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert first_login.status_code == status.HTTP_200_OK
    assert second_login.status_code == status.HTTP_200_OK

    first_token = first_login.json()["session_token"]
    second_token = second_login.json()["session_token"]

    response = client.patch(
        "/auth/logout-all",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == "Logged out successfully from all sessions."

    sessions = db.query(DBSession).filter(DBSession.user_id == user.id).all()

    assert len(sessions) == 2

    for stored_session in sessions:
        assert stored_session.revoked_at is not None

    # First session must be revoked.
    with pytest.raises(HTTPException):
        get_session_by_token(
            first_token,
            db,
        )

    # Second session must also be revoked.
    with pytest.raises(HTTPException):
        get_session_by_token(
            second_token,
            db,
        )


# ============================================================
# SESSION EXPIRATION TESTS
# ============================================================


def test_expired_session_is_rejected(
    client,
    db,
    create_test_user,
):
    email = unique_email("expired_session")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    session_token = login_response.json()["session_token"]

    stored_session = db.query(DBSession).filter(DBSession.user_id == user.id).first()

    assert stored_session is not None

    stored_session.session_expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )

    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        get_session_by_token(
            session_token,
            db,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    assert exc_info.value.detail == "Session expired"

    db.refresh(stored_session)

    assert stored_session.revoked_at is not None


def test_expired_refresh_token_is_rejected(
    client,
    db,
    create_test_user,
):
    email = unique_email("expired_refresh")

    user = create_test_user(
        email=email,
        name="John Doe",
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    refresh_token = login_response.json()["refresh_token"]

    stored_session = db.query(DBSession).filter(DBSession.user_id == user.id).first()

    assert stored_session is not None

    stored_session.refresh_expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )

    db.commit()

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    db.refresh(stored_session)

    assert stored_session.revoked_at is not None
