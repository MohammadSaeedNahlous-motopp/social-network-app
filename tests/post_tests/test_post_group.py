from fastapi import status
from fastapi.responses import FileResponse

from models.enums import GroupRole


def test_group_member_can_delete_own_post(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    owner = create_test_user(
        email="group_owner@example.com",
        name="Group Owner",
    )

    member = authenticated_user(
        email="group_post_owner@example.com",
        name="Post Owner",
    )

    group = create_test_group(
        owner=owner,
        name="Own Post Delete Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "My group post",
            "content": "My content",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    post_id = create_response.json()["id"]

    # Act
    delete_response = client.delete(f"/group_posts/{group.id}/posts/{post_id}")

    # Assert
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == ("Group post deleted successfully.")


def test_group_admin_can_delete_another_members_post(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    admin = create_test_user(
        email="group_admin@example.com",
        name="Admin",
    )

    member = authenticated_user(
        email="member_post@example.com",
        name="Member",
    )

    group = create_test_group(
        owner=admin,
        name="Admin Delete Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=admin,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "Member post",
            "content": "Member content",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    post_id = create_response.json()["id"]

    # Switch authentication from member to group admin
    authenticated_user(
        email=admin.email,
        name=admin.name,
    )

    # Act
    delete_response = client.delete(f"/group_posts/{group.id}/posts/{post_id}")

    # Assert
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == ("Group post deleted successfully.")


def test_normal_member_cannot_delete_another_members_post(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    owner = create_test_user(
        email="permission_group_owner@example.com",
        name="Group Owner",
    )

    post_owner = authenticated_user(
        email="post_owner@example.com",
        name="Post Owner",
    )

    other_member = create_test_user(
        email="other_group_member@example.com",
        name="Other Member",
    )

    group = create_test_group(
        owner=owner,
        name="Member Permission Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
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
        "/group_posts/create",
        data={
            "group_id": group.id,
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
    delete_response = client.delete(f"/group_posts/{group.id}/posts/{post_id}")

    # Assert
    assert delete_response.status_code == status.HTTP_403_FORBIDDEN
    assert delete_response.json()["detail"] == (
        "Only a group administrator or the owner of the post that belongs to a group to can delete this post."
    )


def test_group_member_can_update_own_post(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    owner = create_test_user(
        email="update_group_owner@example.com",
        name="Group Owner",
    )

    member = authenticated_user(
        email="update_post_owner@example.com",
        name="Post Owner",
    )

    group = create_test_group(
        owner=owner,
        name="Update Post Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "Old title",
            "content": "Old content",
        },
    )

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    # Act
    response = client.put(
        f"/group_posts/{post_id}/edit",
        json={
            "group_id": group.id,
            "title": "Updated title",
            "content": "Updated content",
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["content"] == "Updated content"


def test_group_member_can_create_post_with_image(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    generate_test_image,
    get_response_filename
):
    # Arrange
    owner = create_test_user(
        email="image_group_owner@example.com",
        name="Group Owner",
    )

    member = authenticated_user(
        email="image_group_member@example.com",
        name="Group Member",
    )

    group = create_test_group(
        owner=owner,
        name="Image Post Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    image_file = generate_test_image(image_format="png")

    # Act
    response = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "Group post with image",
            "content": "Testing image upload.",
        },
        files={
            "image": (
                "test-image.png",
                image_file,
                "image/png",
            )
        },
    )


    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "Group post with image"

    image_response: FileResponse = client.get(f"/images/post/{response.json()["id"]}/image")
    assert image_response.status_code == status.HTTP_200_OK


def test_get_group_posts_with_pagination(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    owner = create_test_user(
        email="pagination_group_owner@example.com",
        name="Group Owner",
    )

    member = authenticated_user(
        email="pagination_group_member@example.com",
        name="Group Member",
    )

    group = create_test_group(
        owner=owner,
        name="Pagination Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    first_post = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "First Group Post",
            "content": "First content",
        },
    )

    second_post = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "Second Group Post",
            "content": "Second content",
        },
    )

    assert first_post.status_code == status.HTTP_201_CREATED
    assert second_post.status_code == status.HTTP_201_CREATED

    # Act
    response = client.get(
        f"/group_posts/{group.id}/posts",
        params={
            "page": 1,
            "page_size": 10,
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    posts = data["items"]

    assert len(posts) == 2

    assert all(post["group_id"] == group.id for post in posts)

    returned_titles = {post["title"] for post in posts}

    assert returned_titles == {
        "First Group Post",
        "Second Group Post",
    }

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 2
    assert data["total_pages"] == 1


def test_get_group_posts_group_not_found(client, authenticated_user):
    # Arrange
    authenticated_user()

    response = client.get(
        "/group_posts/9999/posts",
        params={
            "page": 1,
            "page_size": 10,
        },
    )
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"


def test_non_member_can_view_posts_in_public_group(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    owner = create_test_user(
        email="public_group_owner@example.com",
        name="Public Group Owner",
    )

    member = authenticated_user(
        email="public_group_member@example.com",
        name="Public Group Member",
    )

    group = create_test_group(
        owner=owner,
        name="Public Visibility Group",
        is_public=True,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "Public Group Post",
            "content": "This post is inside a public group.",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    # Switch authentication to a user who is NOT a group member
    non_member = create_test_user(
        email="public_group_non_member@example.com",
        name="Public Group Non Member",
    )

    authenticated_user(
        email=non_member.email,
        name=non_member.name,
    )

    # Act
    response = client.get(
        f"/group_posts/{group.id}/posts",
        params={
            "page": 1,
            "page_size": 10,
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Public Group Post"
    assert data["total"] == 1


def test_non_member_cannot_view_posts_in_private_group(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    # Arrange
    owner = create_test_user(
        email="private_group_owner@example.com",
        name="Private Group Owner",
    )

    member = authenticated_user(
        email="private_group_member@example.com",
        name="Private Group Member",
    )

    group = create_test_group(
        owner=owner,
        name="Private Visibility Group",
        is_public=False,
    )

    create_test_group_member(
        group=group,
        user=owner,
        role=get_test_group_role(GroupRole.administrator),
    )

    create_test_group_member(
        group=group,
        user=member,
        role=get_test_group_role(GroupRole.member),
    )

    create_response = client.post(
        "/group_posts/create",
        data={
            "group_id": group.id,
            "title": "Private Group Post",
            "content": "Only group members should see this.",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    # Switch authentication to a user who is NOT a group member
    non_member = create_test_user(
        email="private_group_non_member@example.com",
        name="Private Group Non Member",
    )

    authenticated_user(
        email=non_member.email,
        name=non_member.name,
    )

    # Act
    response = client.get(
        f"/group_posts/{group.id}/posts",
        params={
            "page": 1,
            "page_size": 10,
        },
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == (
        "You must be a group member to view posts in this private group."
    )
