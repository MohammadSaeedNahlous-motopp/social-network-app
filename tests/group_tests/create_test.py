from sqlalchemy.orm import Session

from models.group import DBGroup


def test_create_group(client, db: Session, authenticated_user):
    # Arrange
    test_user_email = "test_user@example.com"
    test_user_name = "John Doe"
    user = authenticated_user(email=test_user_email, name=test_user_name)

    group_data = {
        "name": "Python Developers",
        "description": "A group for Python developers",
        "is_public": True,
    }

    # Act
    response = client.post(
        "/groups/",
        json={
            "name": group_data["name"],
            "description": group_data["description"],
            "is_public": group_data["is_public"],
        },
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["name"] == group_data["name"]
    assert data["description"] == group_data["description"]
    assert data["is_public"] is group_data["is_public"]
    assert data["owner"]["name"] == test_user_name
    assert data["owner"]["email"] == test_user_email

    db_group = db.query(DBGroup).filter(
        DBGroup.name == group_data["name"]
    ).first()

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
        json={
            "name": group_data["name"],
            "description": group_data["description"],
            "is_public": group_data["is_public"],
        },
    )

    # Assert
    assert response.status_code == 401
