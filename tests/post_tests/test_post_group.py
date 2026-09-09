from fastapi import status

from models.enums import GroupRole


def test_group_member_can_delete_own_post(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    member = authenticated_user(
        email="group_post_owner@example.com",
        name="Post Owner",
    )

    group = create_test_group(
        owner=member,
        name="Own Post Delete Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        f"/groups/{group.id}/posts",
        data={
            "title": "My group post",
            "content": "My content",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    post_id = create_response.json()["id"]

    # Act
    delete_response = client.delete(
        f"/groups/{group.id}/posts/{post_id}"
    )

    # Assert
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == (
        "Group post deleted successfully."
    )


def test_group_admin_can_delete_another_members_post(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    member = authenticated_user(
        email="member_post@example.com",
        name="Member",
    )

    admin = create_test_user(
        email="group_admin@example.com",
        name="Admin",
    )

    group = create_test_group(
        owner=admin,
        name="Admin Delete Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_test_group_member(
        group=group,
        user=admin,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_response = client.post(
        f"/groups/{group.id}/posts",
        data={
            "title": "Member post",
            "content": "Member content",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    post_id = create_response.json()["id"]

    # Switch authentication from member to admin
    authenticated_user(
        email=admin.email,
        name=admin.name,
    )

    # Act
    delete_response = client.delete(
        f"/groups/{group.id}/posts/{post_id}"
    )

    # Assert
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == (
        "Group post deleted successfully."
    )


def test_normal_member_cannot_delete_another_members_post(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    post_owner = authenticated_user(
        email="post_owner@example.com",
        name="Post Owner",
    )

    other_member = create_test_user(
        email="other_group_member@example.com",
        name="Other Member",
    )

    group = create_test_group(
        owner=post_owner,
        name="Member Permission Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=post_owner,
        role=get_test_group_role(GroupRole.member),
    )

    create_test_group_member(
        group=group,
        user=other_member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        f"/groups/{group.id}/posts",
        data={
            "title": "Owner post",
            "content": "Owner content",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    post_id = create_response.json()["id"]

    # Switch authentication to the other normal member
    authenticated_user(
        email=other_member.email,
        name=other_member.name,
    )

    # Act
    delete_response = client.delete(
        f"/groups/{group.id}/posts/{post_id}"
    )

    # Assert
    assert delete_response.status_code == status.HTTP_403_FORBIDDEN
    assert delete_response.json()["detail"] == (
        "You do not have permission to delete this post."
    )