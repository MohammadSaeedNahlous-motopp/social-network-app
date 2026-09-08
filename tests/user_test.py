from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session

from main import app
from models.enums import Gender
from models.user import DBUser
from auth.oauth2 import get_current_user
from db.hash import Hash


# ============================================================
# HELPERS
# ============================================================


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


# ============================================================
# EDIT USER TESTS
# ============================================================


def test_edit_user_success(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_success_original@example.com",
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

    image = create_test_image()

    response = client.put(
        "/users/edit",
        data={
            "name": "John Updated",
            "email": "edit_success_updated@example.com",
            "bio": "New bio",
            "phone": "0698765432",
            "location": "Amsterdam",
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

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"
    assert data["email"] == "edit_success_updated@example.com"
    assert data["bio"] == "New bio"
    assert data["phone"] == "0698765432"
    assert data["location"] == "Amsterdam"
    assert data["gender"] == "male"
    assert data["profile_img"] is not None

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_success_updated@example.com"
    assert user.bio == "New bio"
    assert user.phone == "0698765432"
    assert user.location == "Amsterdam"
    assert user.gender == Gender.male
    assert user.profile_img is not None

    app.dependency_overrides.clear()


def test_edit_user_without_optional_fields(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_optional_original@example.com",
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
        data={
            "name": "John Updated",
            "email": "edit_optional_updated@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"
    assert data["email"] == "edit_optional_updated@example.com"

    # Optional fields were not sent, so they remain unchanged
    assert data["bio"] == "Old bio"
    assert data["phone"] == "0612345678"
    assert data["location"] == "Rotterdam"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_optional_updated@example.com"
    assert user.bio == "Old bio"
    assert user.phone == "0612345678"
    assert user.location == "Rotterdam"

    app.dependency_overrides.clear()


def test_edit_user_invalid_gender(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_invalid_gender_original@example.com",
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        data={
            "gender": "invalid_gender",
        },
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_edit_user_update_selected_values(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_selected_values_original@example.com",
        password=Hash.hash("password123"),
        bio="Old bio",
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
        data={
            "name": "John Updated",
            "email": "edit_selected_values_updated@example.com",
            "location": "Amsterdam",
            "gender": "female",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"
    assert data["email"] == "edit_selected_values_updated@example.com"
    assert data["location"] == "Amsterdam"
    assert data["gender"] == "female"

    # These weren't sent, so they remain unchanged
    assert data["bio"] == "Old bio"
    assert data["phone"] == "0612345678"
    assert data["profile_img"] == "profile.jpg"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_selected_values_updated@example.com"
    assert user.location == "Amsterdam"
    assert user.gender == Gender.female
    assert user.bio == "Old bio"
    assert user.phone == "0612345678"
    assert user.profile_img == "profile.jpg"

    app.dependency_overrides.clear()


def test_edit_user_empty_optional_fields(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_empty_fields_original@example.com",
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
        data={
            "bio": "",
            "phone": "",
            "location": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Empty values clear these optional fields
    assert data["bio"] is None
    assert data["phone"] is None
    assert data["location"] is None

    # These fields weren't sent, so they remain unchanged
    assert data["name"] == "John Doe"
    assert data["email"] == "edit_empty_fields_original@example.com"
    assert data["gender"] == "male"
    assert data["profile_img"] == "profile.jpg"

    db.refresh(user)

    assert user.bio is None
    assert user.phone is None
    assert user.location is None

    assert user.name == "John Doe"
    assert user.email == "edit_empty_fields_original@example.com"
    assert user.gender == Gender.male
    assert user.profile_img == "profile.jpg"

    app.dependency_overrides.clear()


def test_edit_user_only_email(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_only_email_original@example.com",
        password=Hash.hash("password123"),
        bio="Original bio",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        data={
            "email": "edit_only_email_updated@example.com",
        },
    )

    # Partial update is valid
    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "edit_only_email_updated@example.com"

    # Name and bio weren't sent, so they remain unchanged
    assert data["name"] == "John Doe"
    assert data["bio"] == "Original bio"

    db.refresh(user)

    assert user.email == "edit_only_email_updated@example.com"
    assert user.name == "John Doe"
    assert user.bio == "Original bio"

    app.dependency_overrides.clear()


def test_edit_user_only_name(client, db: Session):
    user = DBUser(
        name="John Doe",
        email="edit_only_name_original@example.com",
        password=Hash.hash("password123"),
        bio="Original bio",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/users/edit",
        data={
            "name": "John Updated",
        },
    )

    # Partial update is valid
    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"

    # Email and bio weren't sent, so they remain unchanged
    assert data["email"] == "edit_only_name_original@example.com"
    assert data["bio"] == "Original bio"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_only_name_original@example.com"
    assert user.bio == "Original bio"

    app.dependency_overrides.clear()


def test_edit_user_unauthorized(client):
    response = client.put(
        "/users/edit",
        data={
            "name": "Unauthorized User",
        },
    )

    assert response.status_code == 401


# ============================================================
# USER ACTIVATION TESTS
# ============================================================


def test_change_activation_to_inactive(client, db: Session):
    user = DBUser(
        name="Activation Inactive User",
        email="activation_to_inactive@example.com",
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
        name="Activation Active User",
        email="activation_to_active@example.com",
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
        name="Activation Toggle User",
        email="activation_toggle_user@example.com",
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


# ============================================================
# PROFILE IMAGE TESTS
# ============================================================


def test_edit_user_profile_image(client, db: Session):
    user = DBUser(
        name="Profile Image User",
        email="profile_image_original@example.com",
        password=Hash.hash("password123"),
        bio="Old bio",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    image = create_test_image()

    response = client.put(
        "/users/edit",
        data={
            "bio": "Updated bio",
        },
        files={
            "profile_img": (
                "new_profile.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["bio"] == "Updated bio"
    assert data["profile_img"] is not None

    db.refresh(user)

    assert user.bio == "Updated bio"
    assert user.profile_img is not None

    app.dependency_overrides.clear()


def test_edit_user_remove_profile_image(client, db: Session):
    user = DBUser(
        name="Remove Image User",
        email="remove_profile_image_original@example.com",
        password=Hash.hash("password123"),
        bio="My bio",
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
        data={
            "remove_profile_img": "true",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["profile_img"] is None

    # Everything else remains unchanged
    assert data["name"] == "Remove Image User"
    assert data["email"] == "remove_profile_image_original@example.com"
    assert data["bio"] == "My bio"
    assert data["phone"] == "0612345678"
    assert data["location"] == "Rotterdam"
    assert data["gender"] == "male"

    db.refresh(user)

    assert user.profile_img is None
    assert user.name == "Remove Image User"
    assert user.email == "remove_profile_image_original@example.com"
    assert user.bio == "My bio"
    assert user.phone == "0612345678"
    assert user.location == "Rotterdam"
    assert user.gender == Gender.male

    app.dependency_overrides.clear()
