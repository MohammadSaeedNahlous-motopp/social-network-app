from models.post import DBPost


def test_create_post(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Test Post",
            "content": "This is a test post.",
            "image_url": None,
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Post"
    assert response.json()["content"] == "This is a test post."
    assert response.json()["image_url"] is None


def test_get_post(client):
    create_response = client.post(
        "/posts/",
        json={
            "title": "Get Post Test",
            "content": "Testing GET.",
            "image_url": None,
        },
    )

    post_id = create_response.json()["id"]

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["id"] == post_id
    assert response.json()["title"] == "Get Post Test"


def test_get_post_not_found(client):
    response = client.get("/posts/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found."


def test_update_post(client):
    create_response = client.post(
        "/posts/",
        json={
            "title": "Old title",
            "content": "Old content",
            "image_url": None,
        },
    )

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


def test_delete_post(client):
    create_response = client.post(
        "/posts/",
        json={
            "title": "Delete me",
            "content": "This post will be deleted.",
            "image_url": None,
        },
    )

    post_id = create_response.json()["id"]

    response = client.delete(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted successfully."

    get_response = client.get(f"/posts/{post_id}")

    assert get_response.status_code == 404
