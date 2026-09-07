import pytest
from fastapi import status

from models.enums import GroupRole
from schemas.user import UserDisplay


@pytest.mark.parametrize(
    "is_public, requester_is_member, expected_status",
    [
        (True, False, status.HTTP_200_OK),
        (True, True, status.HTTP_200_OK),
        (False, True, status.HTTP_200_OK),
        (False, False, status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_group_members_permissions(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    is_public,
    requester_is_member,
    expected_status,
):
    # Arrange
    owner = create_test_user(
        email="members_owner@example.com",
        name="Owner",
    )

    requester = authenticated_user(
        email="members_requester@example.com",
        name="Requester",
    )

    group = create_test_group(
        owner=owner,
        name="Python Developers",
        is_public=is_public,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=GroupRole.administrator,
    )

    if requester_is_member:
        create_test_group_member(
            group=group,
            user=requester,
            role=GroupRole.member,
        )

    # Act
    response = client.get(
        f"/group/{group.id}/members"
    )

    # Assert
    assert response.status_code == expected_status

    if expected_status == status.HTTP_403_FORBIDDEN:
        assert response.json()["detail"] == (
            "User has no permission to read list of group members"
        )


def test_get_group_members(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
):
    # Arrange
    owner = create_test_user(
        email="members_owner@example.com",
        name="Owner",
    )

    requester = authenticated_user(
        email="members_requester@example.com",
        name="Requester",
    )

    member_one = create_test_user(
        email="member_one@example.com",
        name="Member One",
    )

    member_two = create_test_user(
        email="member_two@example.com",
        name="Member Two",
    )

    group = create_test_group(
        owner=owner,
        name="Python Developers",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=GroupRole.administrator,
    )
    create_test_group_member(
        group=group,
        user=requester,
        role=GroupRole.member,
    )
    create_test_group_member(
        group=group,
        user=member_one,
        role=GroupRole.member,
    )
    create_test_group_member(
        group=group,
        user=member_two,
        role=GroupRole.member,
    )

    # Act
    response = client.get(
        f"/group/{group.id}/members"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    # list[tuple[UserDisplay, GroupRole]]
    data = response.json()

    assert len(data) == 4

    emails = {member[0]["email"] for member in data}

    assert emails == {
        owner.email,
        requester.email,
        member_one.email,
        member_two.email,
    }


def test_get_group_members_not_found(
    client,
    authenticated_user,
):
    # Arrange
    authenticated_user(email="members_not_found@example.com")

    # Act
    response = client.get("/group/999999/members")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"


@pytest.mark.parametrize(
    "role",
    [
        GroupRole.member,
        GroupRole.administrator,
    ],
)
def test_is_member(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    role,
):
    # Arrange
    user = authenticated_user(
        email=f"is_member_{role.value}@example.com",
        name="Test User",
    )

    group = create_test_group(
        owner=user,
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=user,
        role=role,
    )

    # Act
    response = client.get(
        f"/group/{group.id}/is_member/{user.id}"
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "is_member": True,
        "role": role.value,
    }


@pytest.mark.parametrize(
    "is_public, requester_is_member, expected_status",
    [
        (True, False, status.HTTP_404_NOT_FOUND),
        (True, True, status.HTTP_404_NOT_FOUND),
        (False, True, status.HTTP_404_NOT_FOUND),
        (False, False, status.HTTP_403_FORBIDDEN),
    ],
)
def test_is_member_user_not_member_or_forbidden(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    is_public,
    requester_is_member,
    expected_status,
):
    # Arrange
    owner = create_test_user(
        email="is_member_owner@example.com",
    )

    requester = authenticated_user(
        email="is_member_requester@example.com",
    )

    target_user = create_test_user(
        email="is_member_target@example.com",
    )

    group = create_test_group(
        owner=owner,
        is_public=is_public,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=GroupRole.administrator,
    )

    if requester_is_member:
        create_test_group_member(
            group=group,
            user=requester,
            role=GroupRole.member,
        )

    # target_user intentionally isn't a member

    # Act
    response = client.get(
        f"/group/{group.id}/is_member/{target_user.id}"
    )

    # Assert
    assert response.status_code == expected_status

    if expected_status == status.HTTP_403_FORBIDDEN:
        assert response.json()["detail"] == "User can't see this group"
    else:
        assert response.json()["detail"] == "User not a group member"


def test_is_member_group_not_found(
    client,
    authenticated_user,
):
    # Arrange
    authenticated_user(email="is_member_not_found@example.com")

    # Act
    response = client.get(
        "/group/999999/is_member/1"
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"
