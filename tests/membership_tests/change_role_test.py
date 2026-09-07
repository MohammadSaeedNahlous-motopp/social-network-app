import pytest
from fastapi import status

from models.enums import GroupRole


@pytest.mark.parametrize(
    "current_role,new_role",
    [
        (GroupRole.member, GroupRole.administrator),
        (GroupRole.administrator, GroupRole.member),
    ],
)
def test_change_user_role(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
    current_role,
    new_role,
):
    # Arrange
    admin = authenticated_user(
        email=f"change_role_admin_{current_role.value}@example.com",
    )

    target_user = create_test_user(
        email=f"change_role_target_{current_role.value}@example.com",
    )

    group = create_test_group(
        owner=admin,
        name="Python Developers",
    )

    create_test_group_member(
        group=group,
        user=admin,
        role=get_test_group_role(GroupRole.administrator),
    )

    membership = create_test_group_member(
        group=group,
        user=target_user,
        role=get_test_group_role(current_role),
    )

    # Act
    response = client.put(
        f"/group/{group.id}/change_role/"
        f"{target_user.id}/{new_role.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "updated_role": new_role.value,
    }

    db.refresh(membership)

    assert membership.role.name == new_role


def test_change_role_forbidden_for_non_admin(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    # Arrange
    owner = create_test_user(
        email="role_owner@example.com",
    )

    issuer = authenticated_user(
        email="role_issuer@example.com",
    )

    target = create_test_user(
        email="role_target@example.com",
    )

    group = create_test_group(
        owner=owner,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=issuer,
        role=get_test_group_role(GroupRole.member),
    )

    target_membership = create_test_group_member(
        group=group,
        user=target,
        role=get_test_group_role(GroupRole.member),
    )

    # Act
    response = client.put(
        f"/group/{group.id}/change_role/"
        f"{target.id}/{GroupRole.administrator.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == (
        "Issuer does not have permission to change the role."
    )

    db.refresh(target_membership)

    assert target_membership.role.name == GroupRole.member


def test_change_role_issuer_not_member(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role
):
    # Arrange
    owner = create_test_user(
        email="role_owner@example.com",
    )

    issuer = authenticated_user(
        email="role_issuer@example.com",
    )

    target = create_test_user(
        email="role_target@example.com",
    )

    group = create_test_group(
        owner=owner,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=target,
        role=get_test_group_role(GroupRole.member),
    )

    # issuer intentionally isn't a member

    # Act
    response = client.put(
        f"/group/{group.id}/change_role/"
        f"{target.id}/{GroupRole.administrator.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == (
        "Issuer is not a group member."
    )


def test_change_role_target_not_member(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role
):
    # Arrange
    admin = authenticated_user(
        email="role_admin@example.com",
    )

    target = create_test_user(
        email="role_target@example.com",
    )

    group = create_test_group(
        owner=admin,
    )

    create_test_group_member(
        group=group,
        user=admin,
        role=get_test_group_role(GroupRole.administrator),
    )

    # target isn't a member

    # Act
    response = client.put(
        f"/group/{group.id}/change_role/"
        f"{target.id}/{GroupRole.administrator.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == (
        "User is not a group member."
    )


@pytest.mark.parametrize(
    "role",
    [
        GroupRole.member,
        GroupRole.administrator,
    ],
)
def test_change_role_same_role(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    role,
):
    # Arrange
    admin = authenticated_user(
        email=f"same_role_admin_{role.value}@example.com",
    )

    target = create_test_user(
        email=f"same_role_target_{role.value}@example.com",
    )

    group = create_test_group(
        owner=admin,
    )

    create_test_group_member(
        group=group,
        user=admin,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=target,
        role=get_test_group_role(role),
    )

    # Act
    response = client.put(
        f"/group/{group.id}/change_role/"
        f"{target.id}/{role.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == (
        "User already has the role."
    )


def test_owner_role_cannot_be_changed(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role
):
    # Arrange
    owner = authenticated_user(
        email="owner_role@example.com",
    )

    group = create_test_group(
        owner=owner,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    # Act
    response = client.put(
        f"/group/{group.id}/change_role/"
        f"{owner.id}/{GroupRole.member.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == (
        "Issuer cannot change the role. "
        f"Group owner role can only be '{GroupRole.administrator}'"
    )


def test_change_role_group_not_found(
    client,
    authenticated_user,
    get_test_group_role
):
    # Arrange
    authenticated_user(
        email="change_role_not_found@example.com",
    )

    # Act
    response = client.put(
        f"/group/999999/change_role/"
        f"1/{GroupRole.member.value}"
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"
