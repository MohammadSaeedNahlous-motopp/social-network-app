from fastapi import status
from sqlalchemy.orm import Session

from models.group import DBGroup


def test_delete_group(
    client,
    authenticated_user,
    create_test_group,
    db: Session,
):
    # Arrange
    user = authenticated_user(email="delete_test@example.com")

    test_group = create_test_group(
        owner=user,
        name="Group to Delete",
        description="Will be deleted",
        is_public=True,
    )

    group_id = test_group.id

    # Act
    response = client.delete(f"/groups/{group_id}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_group = db.query(DBGroup).filter(DBGroup.id == group_id).first()

    assert deleted_group is None


def test_delete_group_forbidden(
    client,
    authenticated_user,
    create_test_group,
    create_test_user,
    db: Session,
):
    # Arrange
    owner = create_test_user(email="delete_owner@example.com")
    authenticated_user(email="delete_other@example.com")

    test_group = create_test_group(
        owner=owner,
        name="Protected Group",
        description="Should not be deleted",
        is_public=True,
    )

    # Act
    response = client.delete(f"/groups/{test_group.id}")

    # Assert
    assert response.json()["detail"] == ("User has no permission to delete group")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    db.refresh(test_group)

    assert db.query(DBGroup).filter(DBGroup.id == test_group.id).first() is not None


def test_delete_group_not_found(
    client,
    authenticated_user,
):
    # Arrange
    authenticated_user(email="delete_not_found@example.com")

    # Act
    response = client.delete("/groups/999999")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"
