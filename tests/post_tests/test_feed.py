from models.friend import DBFriend
from models.post import DBPost


def test_feed_contains_users_own_posts(
    client,
    db,
    authenticated_user,
):
    user = authenticated_user()

    post = DBPost(
        user_id=user.id,
        title="My feed post",
        content="This is my own post",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    response = client.get("/posts/feed?page=1&page_size=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == post.id
    assert data["items"][0]["user_id"] == user.id
    assert data["items"][0]["title"] == "My feed post"


def test_feed_contains_friends_posts(
    client,
    db,
    authenticated_user,
    create_test_user,
):
    current_user = authenticated_user()

    friend = create_test_user(
        email="friend@example.com",
        name="Friend User",
    )

    friendship = DBFriend(
        user_id=current_user.id,
        friend_id=friend.id,
    )

    friend_post = DBPost(
        user_id=friend.id,
        title="Friend post",
        content="Post from my friend",
    )

    db.add_all(
        [
            friendship,
            friend_post,
        ]
    )
    db.commit()
    db.refresh(friend_post)

    response = client.get("/posts/feed?page=1&page_size=10")

    assert response.status_code == 200

    data = response.json()

    post_ids = [post["id"] for post in data["items"]]

    assert friend_post.id in post_ids
