from fastapi import status


# ============================================================
# DELETE FRIEND
# ============================================================


def test_delete_friend_successfully(
    client,
    create_test_user,
    authenticated_user,
):
    user_1 = create_test_user(
        email="delete_friend_user_one@example.com",
        name="Delete Friend User One",
    )

    user_2 = create_test_user(
        email="delete_friend_user_two@example.com",
        name="Delete Friend User Two",
    )

    # Authenticate as User 1
    authenticated_user(
        email=user_1.email,
        name=user_1.name,
    )

    # Send friend request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2.id,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Authenticate as User 2
    authenticated_user(
        email=user_2.email,
        name=user_2.name,
    )

    # Accept request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK

    # Authenticate as User 1
    authenticated_user(
        email=user_1.email,
        name=user_1.name,
    )

    # Get friendship
    response = client.get("/friends/")

    assert response.status_code == status.HTTP_200_OK

    friends = response.json()

    assert len(friends) == 1

    friendship_id = friends[0]["id"]

    # Delete friendship
    response = client.delete(
        f"/friends/{friendship_id}",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == "Friendship was deleted!"

    # User 1 has no friends
    response = client.get("/friends/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    # Authenticate as User 2
    authenticated_user(
        email=user_2.email,
        name=user_2.name,
    )

    # User 2 also has no friends
    response = client.get("/friends/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_cannot_delete_someone_else_friendship(
    client,
    create_test_user,
    authenticated_user,
):
    user_1 = create_test_user(
        email="owner_user_one@example.com",
        name="Owner User One",
    )

    user_2 = create_test_user(
        email="owner_user_two@example.com",
        name="Owner User Two",
    )

    user_3 = create_test_user(
        email="unauthorized_delete_user@example.com",
        name="Unauthorized Delete User",
    )

    # Authenticate as User 1
    authenticated_user(
        email=user_1.email,
        name=user_1.name,
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2.id,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Authenticate as User 2
    authenticated_user(
        email=user_2.email,
        name=user_2.name,
    )

    # User 2 accepts
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK

    # Authenticate as User 1
    authenticated_user(
        email=user_1.email,
        name=user_1.name,
    )

    # Get friendship ID
    response = client.get("/friends/")

    assert response.status_code == status.HTTP_200_OK

    friendship_id = response.json()[0]["id"]

    # Authenticate as User 3
    authenticated_user(
        email=user_3.email,
        name=user_3.name,
    )

    # User 3 tries to delete friendship
    response = client.delete(
        f"/friends/{friendship_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == "Friendship not found!"


def test_delete_nonexistent_friendship(
    client,
    authenticated_user,
):
    authenticated_user(
        email="nonexistent_friendship_user@example.com",
        name="Nonexistent Friendship User",
    )

    response = client.delete("/friends/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == "Friendship not found!"
