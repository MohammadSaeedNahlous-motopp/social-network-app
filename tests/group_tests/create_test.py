from fastapi import status
from sqlalchemy.orm import Session

from models.group import DBGroup


def test_create_group(client, db: Session, authenticated_user, generate_test_image):
    # Arrange
    test_user_email = "test_user@example.com"
    test_user_name = "John Doe"
    user = authenticated_user(email=test_user_email, name=test_user_name)

    group_image = generate_test_image()
    group_background_image = generate_test_image()

    group_data = {
        "name": "Python Developers",
        "description": "A group for Python developers",
        "is_public": True,
        "group_image": {
            "filename": "group_image.jpeg",
            "bytes": group_image,
            "data_type": "image/jpeg",
        },
        "group_background_image": {
            "filename": "group_background_image.jpeg",
            "bytes": group_background_image,
            "data_type": "image/jpeg",
        },
    }

    # Act
    response = client.post(
        "/groups/",
        data={
            "name": group_data["name"],
            "description": group_data["description"],
            "is_public": group_data["is_public"],
        },
        files={
            "group_img": (
                group_data["group_image"]["filename"],
                group_data["group_image"]["bytes"],
                group_data["group_image"]["data_type"],
            ),
            "group_background_img": (
                group_data["group_background_image"]["filename"],
                group_data["group_background_image"]["bytes"],
                group_data["group_background_image"]["data_type"],
            ),
        },
    )

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == group_data["name"]
    assert data["description"] == group_data["description"]
    assert data["is_public"] is group_data["is_public"]
    assert data["owner"]["name"] == test_user_name
    assert data["owner"]["email"] == test_user_email
    assert data["tags"] == []

    db_group = db.query(DBGroup).filter(DBGroup.name == group_data["name"]).first()

    assert db_group is not None
    assert db_group.owner_id == user.id


def test_create_group_unauthorized(client):
    # Arrange
    group_data = {
        "name": "Python Developers",
        "description": "A group for Python developers",
        "is_public": True,
    }

    # Act
    response = client.post(
        "/groups/",
        data={
            "name": group_data["name"],
            "description": group_data["description"],
            "is_public": group_data["is_public"],
        },
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_group_with_tags(
    client,
    db: Session,
    authenticated_user,
    generate_test_image,
):
    user = authenticated_user(
        email="test_user@example.com",
        name="John Doe",
    )

    group_image = generate_test_image()
    group_background_image = generate_test_image()

    response = client.post(
        "/groups/",
        data={
            "name": "Python Developers",
            "description": "A group for Python developers",
            "is_public": True,
            "tags": "1,2,5",
        },
        files={
            "group_img": (
                "group_image.jpeg",
                group_image,
                "image/jpeg",
            ),
            "group_background_img": (
                "group_background_image.jpeg",
                group_background_image,
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Python Developers"

    assert {tag["id"] for tag in data["tags"]} == {1, 2, 5}

    db_group = (
        db.query(DBGroup)
        .filter(DBGroup.name == "Python Developers")
        .first()
    )

    assert db_group is not None
    assert {group_tag.tag_id for group_tag in db_group.tags} == {1, 2, 5}


def test_create_group_with_invalid_tag(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.post(
        "/groups/",
        data={
            "name": "Invalid Tags Group",
            "description": "Test",
            "is_public": True,
            "tags": "1,999",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid tag IDs"
