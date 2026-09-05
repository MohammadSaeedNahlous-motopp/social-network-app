from sqlalchemy.orm import Session

from main import app
from models.user import DBUser
from models.group import DBGroup
from auth.oauth2 import get_current_user
from db.hash import Hash


def create_test_user(db: Session, email="group_test@example.com"):
    user = DBUser(
        name="John Doe",
        email=email,
        password=Hash.hash("password123"),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def test_create_group(client, db: Session):
    user = create_test_user(db)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        "/groups/",
        json={
            "name": "Python Developers",
            "description": "A group for Python developers",
            "is_public": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Python Developers"
    assert data["description"] == "A group for Python developers"
    assert data["is_public"] is True
    assert data["owner"]["name"] == "John Doe"
    assert data["owner"]["email"] == "group_test@example.com"

    db_group = db.query(DBGroup).filter(
        DBGroup.name == "Python Developers"
    ).first()

    assert db_group is not None
    assert db_group.owner_id == user.id

    app.dependency_overrides.clear()


def test_create_group_unauthorized(client):
    response = client.post(
        "/groups/",
        json={
            "name": "Python Developers",
            "description": "A group for Python developers",
            "is_public": True,
        },
    )

    assert response.status_code == 401


def test_get_group_by_id(client, db: Session):
    user = create_test_user(db, "get_group@example.com")

    db_group = DBGroup(
        name="Python Developers",
        description="Python group",
        owner_id=user.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    response = client.get(f"/groups/{db_group.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == db_group.id
    assert data["name"] == "Python Developers"
    assert data["description"] == "Python group"
    assert data["owner"]["name"] == "John Doe"
    assert data["owner"]["email"] == "get_group@example.com"


def test_get_group_by_id_not_found(client):
    response = client.get("/groups/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_update_group_success(client, db: Session):
    user = create_test_user(db, "update_group@example.com")

    db_group = DBGroup(
        name="Old Name",
        description="Old description",
        owner_id=user.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        f"/groups/edit/{db_group.id}",
        json={
            "name": "New Name",
            "description": "New description",
            "is_public": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "New Name"
    assert data["description"] == "New description"
    assert data["is_public"] is False

    db.refresh(db_group)

    assert db_group.name == "New Name"
    assert db_group.description == "New description"
    assert db_group.is_public is False

    app.dependency_overrides.clear()


def test_update_group_forbidden(client, db: Session):
    owner = create_test_user(db, "group_owner@example.com")
    other_user = create_test_user(db, "other_user@example.com")

    db_group = DBGroup(
        name="Original Name",
        description="Original description",
        owner_id=owner.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    app.dependency_overrides[get_current_user] = lambda: other_user

    response = client.put(
        f"/groups/edit/{db_group.id}",
        json={
            "name": "Hacked Name",
        },
    )

    assert response.status_code == 403

    db.refresh(db_group)

    assert db_group.name == "Original Name"

    app.dependency_overrides.clear()


def test_update_group_not_found(client, db: Session):
    user = create_test_user(db, "update_not_found@example.com")

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        "/groups/edit/999999",
        json={
            "name": "New Name",
        },
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_update_group_empty_request(client, db: Session):
    user = create_test_user(db, "empty_update@example.com")

    db_group = DBGroup(
        name="Original",
        description="Description",
        owner_id=user.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.put(
        f"/groups/edit/{db_group.id}",
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "At least one field must be provided for update"
    )

    app.dependency_overrides.clear()


def test_delete_group_success(client, db: Session):
    user = create_test_user(db, "delete_group@example.com")

    db_group = DBGroup(
        name="Group to Delete",
        description="Will be deleted",
        owner_id=user.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    group_id = db_group.id

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete(f"/groups/{group_id}")

    assert response.status_code == 200
    assert response.json() == "Ok"

    deleted_group = db.query(DBGroup).filter(
        DBGroup.id == group_id
    ).first()

    assert deleted_group is None

    app.dependency_overrides.clear()


def test_delete_group_forbidden(client, db: Session):
    owner = create_test_user(db, "delete_owner@example.com")
    other_user = create_test_user(db, "delete_other@example.com")

    db_group = DBGroup(
        name="Protected Group",
        description="Should not be deleted",
        owner_id=owner.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    app.dependency_overrides[get_current_user] = lambda: other_user

    response = client.delete(f"/groups/{db_group.id}")

    assert response.status_code == 403

    assert db.query(DBGroup).filter(
        DBGroup.id == db_group.id
    ).first() is not None

    app.dependency_overrides.clear()


def test_delete_group_not_found(client, db: Session):
    user = create_test_user(db, "delete_not_found@example.com")

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete("/groups/999999")

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_search_groups_by_name(client, db: Session):
    user = create_test_user(db, "search_name@example.com")

    groups = [
        DBGroup(
            name="Python Developers",
            description="Programming group",
            owner_id=user.id,
            is_public=True,
        ),
        DBGroup(
            name="Java Developers",
            description="Programming group",
            owner_id=user.id,
            is_public=True,
        ),
        DBGroup(
            name="Cooking Club",
            description="Food enthusiasts",
            owner_id=user.id,
            is_public=True,
        ),
    ]

    db.add_all(groups)
    db.commit()

    response = client.get(
        "/groups/search",
        params={"name": "python"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Python Developers"


def test_search_groups_case_insensitive(client, db: Session):
    user = create_test_user(db, "search_case@example.com")

    db_group = DBGroup(
        name="Python Developers",
        description="Programming group",
        owner_id=user.id,
        is_public=True,
    )

    db.add(db_group)
    db.commit()

    response = client.get(
        "/groups/search",
        params={"name": "PYTHON"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Python Developers"


def test_search_groups_matches_whole_search_string(client, db: Session):
    user = create_test_user(db, "search_whole_string@example.com")

    groups = [
        DBGroup(
            name="Python Developers",
            description="Programming",
            owner_id=user.id,
            is_public=True,
        ),
        DBGroup(
            name="Python Community for Developers",
            description="Programming",
            owner_id=user.id,
            is_public=True,
        ),
    ]

    db.add_all(groups)
    db.commit()

    response = client.get(
        "/groups/search",
        params={"name": "python developers"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Python Developers"


def test_search_groups_without_parameters(client, db: Session):
    response = client.get("/groups/search")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "At least one field must be provided for search"
    )


