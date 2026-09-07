import pytest
from fastapi import status

from models.enums import GroupRole
from models.group_member import DBGroupMember


@pytest.mark.parametrize(
    "is_public, expected_status",
    [
        (True, status.HTTP_200_OK),
        (False, status.HTTP_501_NOT_IMPLEMENTED),
    ],
)
def test_join_group(
    client,
    authenticated_user,
    create_test_group,
    db,
    is_public,
    expected_status,
):
    # Arrange
    user = authenticated_user(
        email=f"join_{is_public}@example.com",
        name="Joining User",
    )

    group = create_test_group(
        owner=create_test_group.__wrapped__.__defaults__[0]
        if False
        else user,
        name="Python Developers",
        is_public=is_public,
    )

    # Act
    response = client.post(
        f"/group/{group.id}/join"
    )

    # Assert
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        data = response.json()

        assert data["email"] == user.email
        assert data["name"] == user.name

        membership = (
            db.query(DBGroupMember)
            .filter(
                DBGroupMember.group_id == group.id,
                DBGroupMember.user_id == user.id,
            )
            .first()
        )

        assert membership is not None
        assert membership.role == GroupRole.member

    elif response.status_code == status.HTTP_501_NOT_IMPLEMENTED:
        assert response.json()["detail"] == (
            "Join request for private groups is not implemented"
        )


def test_join_group_already_member(
    client,
    authenticated_user,
    create_test_group,
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
        role=GroupRole.member,
    )

    # Act
    response = client.post(
        f"/group/{group.id}/join"
    )

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == (
        "User already has joined a group."
    )


def test_join_group_not_found(
    client,
    authenticated_user,
):
    # Arrange
    authenticated_user(
        email="join_not_found@example.com",
    )

    # Act
    response = client.post(
        "/group/999999/join"
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"
