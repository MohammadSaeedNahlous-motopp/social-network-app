import pytest
from fastapi import status

from models.enums import GroupRole
from models.group_member import DBGroupMember


@pytest.mark.parametrize(
    "role",
    [
        GroupRole.member,
        GroupRole.administrator,
    ],
)
def test_leave_group(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
    role,
):
    # Arrange
    owner = create_test_user(
        email=f"leave_owner_{role.value}@example.com",
    )

    user = authenticated_user(
        email=f"leave_user_{role.value}@example.com",
    )

    group = create_test_group(
        owner=owner,
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    membership = create_test_group_member(
        group=group,
        user=user,
        role=get_test_group_role(role),
    )

    membership_id = membership.id

    # Act
    response = client.post(
        f"/group/{group.id}/leave"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "is_member": False,
    }

    deleted_membership = (
        db.query(DBGroupMember)
        .filter(DBGroupMember.id == membership_id)
        .first()
    )

    assert deleted_membership is None


def test_owner_cannot_leave_group(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role
):
    # Arrange
    owner = authenticated_user(
        email="leave_owner@example.com",
    )

    group = create_test_group(
        owner=owner,
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    # Act
    response = client.post(
        f"/group/{group.id}/leave"
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == (
        "User cannot leave group he owns."
    )


def test_leave_group_not_member(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role
):
    # Arrange
    owner = create_test_user(
        email="leave_owner@example.com",
    )

    authenticated_user(
        email="leave_non_member@example.com",
    )

    group = create_test_group(
        owner=owner,
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    # user isn't a group member

    # Act
    response = client.post(
        f"/group/{group.id}/leave"
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == (
        "User is not a member of this group."
    )
