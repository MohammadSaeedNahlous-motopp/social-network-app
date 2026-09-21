from io import BytesIO

from PIL import Image


def test_create_post(client, authenticated_user):
    user = authenticated_user()

    response = client.post(
        "/posts/",
        data={
            "title": "Test Post",
            "content": "This is a test post.",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Post"
    assert response.json()["content"] == "This is a test post."
    assert response.json()["user_id"] == user.id
    assert response.json()["visibility"] == "public"


def test_get_post(client, authenticated_user):
    authenticated_user()

    image_file = BytesIO()

    image = Image.new("RGB", (10, 10))
    image.save(image_file, format="PNG")
    image_file.seek(0)

    create_response = client.post(
        "/posts/",
        data={
            "title": "Get Post Test",
            "content": "Testing GET.",
        },
        files={
            "image": (
                "test-image.png",
                image_file,
                "image/png",
            )
        },
    )

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["id"] == post_id
    assert response.json()["title"] == "Get Post Test"
    assert response.json()["content"] == "Testing GET."


def test_get_post_not_found(client):
    response = client.get("/posts/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found."


def test_update_post(client, authenticated_user):
    authenticated_user()

    create_response = client.post(
        "/posts/",
        data={
            "title": "Old title",
            "content": "Old content",
        },
    )

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "Updated title",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["content"] == "Old content"


def test_delete_post(client, authenticated_user):
    authenticated_user()

    create_response = client.post(
        "/posts/",
        data={
            "title": "Delete me",
            "content": "This post will be deleted.",
        },
    )

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.delete(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted successfully."

    get_response = client.get(f"/posts/{post_id}")

    assert get_response.status_code == 404


def test_get_user_posts(client, authenticated_user):
    user = authenticated_user()

    first_post = client.post(
        "/posts/",
        data={
            "title": "First Post",
            "content": "My first wall post.",
        },
    )

    second_post = client.post(
        "/posts/",
        data={
            "title": "Second Post",
            "content": "My second wall post.",
            "visibility": "friends_only",
        },
    )

    assert first_post.status_code == 201
    assert second_post.status_code == 201

    response = client.get(
        f"/posts/{user.id}/all",
        params={
            "page": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()
    posts = data["items"]

    assert len(posts) == 2

    assert all(post["user_id"] == user.id for post in posts)

    returned_titles = {post["title"] for post in posts}

    assert returned_titles == {
        first_post.json()["title"],
        second_post.json()["title"],
    }

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 2
    assert data["total_pages"] == 1


def test_create_friends_only_post(client, authenticated_user):
    user = authenticated_user()

    response = client.post(
        "/posts/",
        data={
            "title": "Friends Only Post",
            "content": "Only my friends should see this.",
            "visibility": "friends_only",
        },
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == user.id
    assert response.json()["visibility"] == "friends_only"


def test_non_friend_can_only_see_public_posts(
    client,
    authenticated_user,
    create_test_user,
):
    # Arrange
    post_owner = authenticated_user(
        email="visibility_owner@example.com",
        name="Visibility Owner",
    )

    public_post = client.post(
        "/posts/",
        data={
            "title": "Public Post",
            "content": "Everyone can see this.",
            "visibility": "public",
        },
    )

    friends_only_post = client.post(
        "/posts/",
        data={
            "title": "Friends Only Post",
            "content": "Friends should see this.",
            "visibility": "friends_only",
        },
    )

    assert public_post.status_code == 201
    assert friends_only_post.status_code == 201

    non_friend = create_test_user(
        email="visibility_non_friend@example.com",
        name="Non Friend",
    )

    # Switch authentication to the non-friend
    authenticated_user(
        email=non_friend.email,
        name=non_friend.name,
    )

    # Act
    response = client.get(
        f"/posts/{post_owner.id}/all",
        params={
            "page": 1,
            "page_size": 10,
        },
    )

    # Assert
    assert response.status_code == 200

    data = response.json()
    posts = data["items"]

    assert len(posts) == 1
    assert posts[0]["title"] == "Public Post"
    assert posts[0]["visibility"] == "public"

    assert data["total"] == 1
    assert data["total_pages"] == 1
