from models.comment import DBComment
from models.post import DBPost


def test_post_owner_can_create_comment(
    client,
    db,
    authenticated_user,
):
    user = authenticated_user()

    post = DBPost(
        user_id=user.id,
        title="Test post",
        content="Test content",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    response = client.post(
        f"/comments/posts/{post.id}",
        json={
            "content": "This is my comment.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["content"] == "This is my comment."
    assert data["user_id"] == user.id
    assert data["name"] == user.name
    assert data["post_id"] == post.id
    assert data["is_visible"] is True


def test_created_comment_is_saved_in_database(
    client,
    db,
    authenticated_user,
):
    user = authenticated_user()

    post = DBPost(
        user_id=user.id,
        title="Test post",
        content="Test content",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    response = client.post(
        f"/comments/posts/{post.id}",
        json={
            "content": "Database test comment.",
        },
    )

    assert response.status_code == 201

    comment = (
        db.query(DBComment)
        .filter(DBComment.post_id == post.id)
        .first()
    )

    assert comment is not None
    assert comment.content == "Database test comment."
    assert comment.user_id == user.id
    assert comment.is_visible is True


def test_get_comments_by_post(
    client,
    db,
    authenticated_user,
):
    user = authenticated_user()

    post = DBPost(
        user_id=user.id,
        title="Test post",
        content="Test content",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    comment_1 = DBComment(
        user_id=user.id,
        post_id=post.id,
        content="First comment",
    )

    comment_2 = DBComment(
        user_id=user.id,
        post_id=post.id,
        content="Second comment",
    )

    db.add_all([comment_1, comment_2])
    db.commit()

    response = client.get(
        f"/comments/posts/{post.id}?offset=0"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["content"] == "First comment"
    assert data["items"][0]["user_id"] == user.id
    assert data["items"][0]["name"] == user.name
    assert data["items"][0]["post_id"] == post.id

    assert data["items"][1]["content"] == "Second comment"

    assert data["has_more"] is False
    assert data["next_offset"] is None


def test_get_comments_pagination(
    client,
    db,
    authenticated_user,
):
    user = authenticated_user()

    post = DBPost(
        user_id=user.id,
        title="Pagination test post",
        content="Test content",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    comments = [
        DBComment(
            user_id=user.id,
            post_id=post.id,
            content=f"Comment {i}",
        )
        for i in range(18)
    ]

    db.add_all(comments)
    db.commit()

    # First batch
    response = client.get(
        f"/comments/posts/{post.id}?offset=0"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 10
    assert data["has_more"] is True
    assert data["next_offset"] == 10

    # Second batch
    response = client.get(
        f"/comments/posts/{post.id}?offset=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 8
    assert data["has_more"] is False
    assert data["next_offset"] is None


def test_comment_owner_can_delete_own_comment(
    client,
    db,
    authenticated_user
):
    user = authenticated_user()

    post = DBPost(
        user_id=user.id,
        title="Test post",
        content="Test content"
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    comment = DBComment(
        user_id=user.id,
        post_id=post.id,
        content="Comment to delete",
        is_visible=True,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    response = client.delete(
        f"/comments/{comment.id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Comment deleted successfully."
    }

    db.refresh(comment)

    assert comment.is_visible is False


def test_create_comment_post_not_found(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.post(
        "/comments/posts/999999",
        json={
            "content": "Comment",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found."


def test_get_comments_post_not_found(
    client,
):
    response = client.get(
        "/comments/posts/999999?offset=0"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found."