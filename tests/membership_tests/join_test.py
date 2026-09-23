import pytest
from fastapi import status

from models.enums import GroupRole, RequestStatus
from models.group_member import DBGroupMember
from tests.conftest import create_test_user


@pytest.mark.parametrize(
    "is_public",
    [
        True,
        False,
    ],
)
def test_join_group(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    get_test_group_role,
    db,
    is_public,
):
    # Arrange
    user = authenticated_user(
        email=f"join_{is_public}@example.com",
        name="Joining User",
    )

    owner = create_test_user(email="owner@example.com", name="Owner")

    group = create_test_group(
        owner=owner,
        name="Python Developers",
        is_public=is_public,
    )

    # Act
    response = client.post(f"/group/{group.id}/join")

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    if is_public:

        assert data["group_id"] == group.id
        assert data["user_id"] == user.id
        assert data["role"] == GroupRole.member

        membership = (
            db.query(DBGroupMember)
            .filter(
                DBGroupMember.group_id == group.id,
                DBGroupMember.user_id == user.id,
            )
            .first()
        )

        assert membership is not None
        assert membership.role.name == GroupRole.member

    else:
        assert data["group"]["id"] == group.id
        assert data["sender"]["id"] == user.id
        assert data["status"] == RequestStatus.pending

def test_join_group_already_member(
    client,
    authenticated_user,
    create_test_group,
    get_test_group_role,
    create_test_group_member,
):
    # Arrange
    user = authenticated_user(
        email="already_member@example.com",
    )

    group = create_test_group(
        owner=user,
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=user,
        role=get_test_group_role(GroupRole.member),
    )

    # Act
    response = client.post(f"/group/{group.id}/join")

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == ("User already has joined a group.")


def test_join_group_not_found(
    client,
    authenticated_user,
):
    # Arrange
    authenticated_user(
        email="join_not_found@example.com",
    )

    # Act
    response = client.post("/group/999999/join")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"
