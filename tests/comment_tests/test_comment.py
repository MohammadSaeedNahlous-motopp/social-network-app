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


def test_comment_owner_can_delete_own_comment(
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

    comment = DBComment(
        user_id=user.id,
        post_id=post.id,
        content="Comment to delete",
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    response = client.delete(
        f"/comments/{comment.id}",
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