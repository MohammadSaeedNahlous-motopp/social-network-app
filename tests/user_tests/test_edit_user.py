from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session

from models.enums import Gender


def create_test_image(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size)
    image_bytes = BytesIO()

    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


# ============================================================
# EDIT USER TESTS
# ============================================================


def test_edit_user_success(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="edit_success_original@example.com",
        name="John Doe",
    )

    user.bio = "Old bio"
    user.phone = "0612345678"
    user.location = "Rotterdam"
    user.gender = Gender.male

    db.commit()
    db.refresh(user)

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


def test_edit_user_without_optional_fields(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="edit_optional_original@example.com",
        name="John Doe",
    )

    user.bio = "Old bio"
    user.phone = "0612345678"
    user.location = "Rotterdam"

    db.commit()
    db.refresh(user)

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

    assert data["bio"] == "Old bio"
    assert data["phone"] == "0612345678"
    assert data["location"] == "Rotterdam"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_optional_updated@example.com"
    assert user.bio == "Old bio"
    assert user.phone == "0612345678"
    assert user.location == "Rotterdam"


def test_edit_user_invalid_gender(
    client,
    authenticated_user,
):
    authenticated_user(
        email="edit_invalid_gender@example.com",
        name="John Doe",
    )

    response = client.put(
        "/users/edit",
        data={
            "gender": "invalid_gender",
        },
    )

    assert response.status_code == 422


def test_edit_user_update_selected_values(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="edit_selected_values_original@example.com",
        name="John Doe",
    )

    user.bio = "Old bio"
    user.phone = "0612345678"
    user.profile_img = "profile.jpg"
    user.location = "Rotterdam"
    user.gender = Gender.male

    db.commit()
    db.refresh(user)

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


def test_edit_user_empty_optional_fields(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="edit_empty_fields_original@example.com",
        name="John Doe",
    )

    user.bio = "This is my old bio"
    user.phone = "0612345678"
    user.profile_img = "profile.jpg"
    user.location = "Rotterdam"
    user.gender = Gender.male

    db.commit()
    db.refresh(user)

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

    assert data["bio"] is None
    assert data["phone"] is None
    assert data["location"] is None

    assert data["name"] == "John Doe"
    assert data["email"] == "edit_empty_fields_original@example.com"
    assert data["gender"] == "male"
    assert data["profile_img"] == "profile.jpg"

    db.refresh(user)

    assert user.bio is None
    assert user.phone is None
    assert user.location is None


def test_edit_user_only_email(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="edit_only_email_original@example.com",
        name="John Doe",
    )

    user.bio = "Original bio"

    db.commit()
    db.refresh(user)

    response = client.put(
        "/users/edit",
        data={
            "email": "edit_only_email_updated@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "edit_only_email_updated@example.com"
    assert data["name"] == "John Doe"
    assert data["bio"] == "Original bio"

    db.refresh(user)

    assert user.email == "edit_only_email_updated@example.com"
    assert user.name == "John Doe"
    assert user.bio == "Original bio"


def test_edit_user_only_name(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="edit_only_name_original@example.com",
        name="John Doe",
    )

    user.bio = "Original bio"

    db.commit()
    db.refresh(user)

    response = client.put(
        "/users/edit",
        data={
            "name": "John Updated",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "John Updated"
    assert data["email"] == "edit_only_name_original@example.com"
    assert data["bio"] == "Original bio"

    db.refresh(user)

    assert user.name == "John Updated"
    assert user.email == "edit_only_name_original@example.com"
    assert user.bio == "Original bio"


def test_edit_user_unauthorized(client):
    response = client.put(
        "/users/edit",
        data={
            "name": "Unauthorized User",
        },
    )

    assert response.status_code == 401
