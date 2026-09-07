from fastapi import status

from tests.friend_request_test import create_test_user


# ============================================================
# FRIENDS TESTS
# ============================================================


def test_get_friends_successfully(client):
    user_1 = create_test_user(
        client,
        "Friends List User One",
        "friends_list_user_one@example.com",
    )

    user_2 = create_test_user(
        client,
        "Friends List User Two",
        "friends_list_user_two@example.com",
    )

    # User 1 sends a friend request to User 2
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 2 accepts the friend request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    # User 1 gets their friends
    response = client.get(
        "/friends/",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1

    assert data[0]["friend"]["id"] == user_2["user_id"]
    assert data[0]["friend"]["name"] == "Friends List User Two"


# ============================================================
# GET FRIENDS - EMPTY LIST
# ============================================================


def test_get_friends_returns_empty_list(client):
    user = create_test_user(
        client,
        "No Friends User",
        "no_friends_user@example.com",
    )

    response = client.get(
        "/friends/",
        headers=user["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []


# ============================================================
# DELETE FRIEND SUCCESSFULLY
# ============================================================


def test_delete_friend_successfully(client):
    user_1 = create_test_user(
        client,
        "Delete Friend User One",
        "delete_friend_user_one@example.com",
    )

    user_2 = create_test_user(
        client,
        "Delete Friend User Two",
        "delete_friend_user_two@example.com",
    )

    # User 1 sends a friend request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 2 accepts the request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    # Get User 1's friendship record
    response = client.get(
        "/friends/",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    friends = response.json()

    assert len(friends) == 1

    friendship_id = friends[0]["id"]

    # User 1 deletes the friendship
    response = client.delete(
        f"/friends/{friendship_id}",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == "Friendship was deleted!"

    # Check that User 1 has no friends anymore
    response = client.get(
        "/friends/",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []

    # Check that User 2 also has no friends anymore
    response = client.get(
        "/friends/",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []


# ============================================================
# CANNOT DELETE SOMEONE ELSE'S FRIENDSHIP
# ============================================================


def test_cannot_delete_someone_else_friendship(client):
    user_1 = create_test_user(
        client,
        "Owner User One",
        "owner_user_one@example.com",
    )

    user_2 = create_test_user(
        client,
        "Owner User Two",
        "owner_user_two@example.com",
    )

    user_3 = create_test_user(
        client,
        "Unauthorized Delete User",
        "unauthorized_delete_user@example.com",
    )

    # User 1 sends a friend request to User 2
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 2 accepts
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    # Get User 1's friendship ID
    response = client.get(
        "/friends/",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    friendship_id = response.json()[0]["id"]

    # User 3 tries to delete User 1's friendship
    response = client.delete(
        f"/friends/{friendship_id}",
        headers=user_3["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == "Friendship not found!"


# ============================================================
# DELETE NONEXISTENT FRIENDSHIP
# ============================================================


def test_delete_nonexistent_friendship(client):
    user = create_test_user(
        client,
        "Nonexistent Friendship User",
        "nonexistent_friendship_user@example.com",
    )

    response = client.delete(
        "/friends/999999",
        headers=user["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == "Friendship not found!"


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


def test_get_friends_without_authentication(client):
    response = client.get(
        "/friends/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_friend_without_authentication(client):
    response = client.delete(
        "/friends/1",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
