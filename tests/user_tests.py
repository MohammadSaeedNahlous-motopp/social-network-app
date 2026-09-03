from sqlalchemy.orm import Session

from main import app
from models.enums import Gender
from models.user import DBUser
from auth.oauth2 import get_current_user
from db.hash import Hash


def test_edit_user_success(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_test@example.com",
        password=Hash.hash("password123"),
        bio="Old bio",
        phone="0612345678",
        location="Rotterdam",
        gender=Gender.male,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        json={
            "name": "John Updated",
            "email": "updated@example.com",
            "bio": "New bio",
            "phone": "0698765432",
            "location": "Amsterdam",
            "gender": "male",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"
    assert data["email"] == "updated@example.com"
    assert data["bio"] == "New bio"
    assert data["phone"] == "0698765432"
    assert data["location"] == "Amsterdam"
    assert data["gender"] == "male"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "updated@example.com"
    assert user.bio == "New bio"
    assert user.phone == "0698765432"
    assert user.location == "Amsterdam"
    assert user.gender == Gender.male

    app.dependency_overrides.clear()


def test_edit_user_without_optional_fields(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_optional@example.com",
        password=Hash.hash("password123"),
        bio="Old bio",
        phone="0612345678",
        location="Rotterdam",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        json={"name": "John Updated", "email": "edit_optional_updated@example.com"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"
    assert data["email"] == "edit_optional_updated@example.com"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_optional_updated@example.com"

    app.dependency_overrides.clear()


def test_edit_user_invalid_gender(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_gender@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        json={
            "name": "John Doe",
            "email": "edit_gender@example.com",
            "gender": "invalid_gender",
        },
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_edit_user_empty_optional_fields(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="empty_fields@example.com",
        password=Hash.hash("password123"),
        bio="This is my old bio",
        phone="0612345678",
        profile_img="profile.jpg",
        location="Rotterdam",
        gender=Gender.male,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        json={
            "name": "John Doe",
            "email": "empty_fields@example.com",
            "bio": None,
            "phone": None,
            "profile_img": None,
            "location": None,
            "gender": None,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["bio"] is None
    assert data["phone"] is None
    assert data["profile_img"] is None
    assert data["location"] is None
    assert data["gender"] is None

    db.refresh(user)

    assert user.bio is None
    assert user.phone is None
    assert user.profile_img is None
    assert user.location is None
    assert user.gender is None

    app.dependency_overrides.clear()


def test_edit_user_missing_name(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_missing_name@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit", json={"email": "edit_missing_name@example.com"}
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_edit_user_missing_email(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_missing_email@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put("/users/edit", json={"name": "John Updated"})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_edit_user_unauthorized(client):
    response = client.put(
        "/users/edit", json={"name": "John Updated", "email": "updated@example.com"}
    )

    assert response.status_code == 401


def test_change_activation_to_inactive(client, db: Session):
    user = DBUser(
        name="Johnqq Doe",
        email="activationqq_inactive@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    db.refresh(user)
    assert user.is_active is False

    app.dependency_overrides.clear()


def test_change_activation_to_active(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="activationwwww_active333333@example.com",
        password=Hash.hash("password123"),
        is_active=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    db.refresh(user)
    assert user.is_active is True

    app.dependency_overrides.clear()


def test_change_activation_toggle(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="activatiosssssssn_toggle@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    # True -> False
    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # False -> True
    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    db.refresh(user)
    assert user.is_active is True

    app.dependency_overrides.clear()


def test_change_activation_unauthorized(client):
    response = client.patch("/users/toggle-active")

    assert response.status_code == 401
