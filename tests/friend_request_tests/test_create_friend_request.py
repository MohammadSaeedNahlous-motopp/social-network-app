from fastapi import status


def test_create_friend_request_successfully(
    client,
    create_test_user,
    authenticated_user,
):
    user_1 = authenticated_user(
        email="create_success_user1@example.com",
        name="User One",
    )

    user_2 = create_test_user(
        email="create_success_user2@example.com",
        name="User Two",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["status"] == "pending"


def test_cannot_send_friend_request_to_yourself(
    client,
    authenticated_user,
):
    user = authenticated_user(
        email="self_request_user@example.com",
        name="Self Request User",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user.id},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "You cannot send a friend request to yourself!"
    )


def test_cannot_send_friend_request_to_nonexistent_user(
    client,
    authenticated_user,
):
    authenticated_user(
        email="nonexistent_sender@example.com",
        name="Nonexistent Sender",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": 999999},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == "User not found!"


def test_cannot_send_duplicate_friend_request(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="duplicate_user1@example.com",
        name="Duplicate User One",
    )

    user_2 = create_test_user(
        email="duplicate_user2@example.com",
        name="Duplicate User Two",
    )

    # First request
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Duplicate request
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "A pending friend request already exists between these users!"
    )


def test_cannot_send_reverse_friend_request_when_pending_request_exists(
    client,
    create_test_user,
    authenticated_user,
):
    user_1 = authenticated_user(
        email="reverse_user1@example.com",
        name="Reverse User One",
    )

    user_2 = create_test_user(
        email="reverse_user2@example.com",
        name="Reverse User Two",
    )

    # User 1 sends request to User 2
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Switch authentication to User 2
    authenticated_user(email=user_2.email)

    # User 2 tries to send a request back
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_1.id},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "A pending friend request already exists between these users!"
    )
