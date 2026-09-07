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
    assert response.json()["image_url"] is None
    assert response.json()["user_id"] == user.id


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
            "image":(
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
    assert response.json()["image_url"] is not None
    assert response.json()["image_url"].endswith(".png")


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
    assert response.json()["image_url"] is None


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

    response = client.patch(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted successfully."

    get_response = client.get(f"/posts/{post_id}")

    assert get_response.status_code == 404
