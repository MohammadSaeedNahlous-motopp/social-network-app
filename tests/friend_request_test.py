from fastapi import status


# ============================================================
# HELPERS
# ============================================================


def register_user(client, name, email, password="password123"):
    response = client.post(
        "/auth/register",
        data={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
    )

    return response.json()


def login_user(client, email, password="password123"):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    return response.json()


def get_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_test_user(client, name, email, password="password123"):
    register_user(client, name, email, password)

    login_data = login_user(client, email, password)

    return {
        "user_id": login_data["user_id"],
        "email": email,
        "token": login_data["access_token"],
        "headers": get_auth_headers(login_data["access_token"]),
    }


# ============================================================
# CREATE FRIEND REQUEST
# ============================================================


def test_create_friend_request_successfully(client):
    user_1 = create_test_user(
        client,
        "User One",
        "create_success_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "User Two",
        "create_success_user2@example.com",
    )

    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["status"] == "pending"


def test_cannot_send_friend_request_to_yourself(client):
    user_1 = create_test_user(
        client,
        "Self Request User",
        "self_request_user@example.com",
    )

    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_1["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "You cannot send a friend request to yourself!"
    )


def test_cannot_send_friend_request_to_nonexistent_user(client):
    user_1 = create_test_user(
        client,
        "Nonexistent Sender",
        "nonexistent_sender@example.com",
    )

    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": 999999,
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == "User not found!"


def test_cannot_send_duplicate_friend_request(client):
    user_1 = create_test_user(
        client,
        "Duplicate User One",
        "duplicate_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Duplicate User Two",
        "duplicate_user2@example.com",
    )

    # First request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Duplicate request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "A pending friend request already exists between these users!"
    )


def test_cannot_send_reverse_friend_request_when_pending_request_exists(client):
    user_1 = create_test_user(
        client,
        "Reverse User One",
        "reverse_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Reverse User Two",
        "reverse_user2@example.com",
    )

    # User 1 sends request to User 2
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    # User 2 tries to send a request back to User 1
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_1["user_id"],
        },
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "A pending friend request already exists between these users!"
    )


# ============================================================
# GET PENDING FRIEND REQUESTS
# ============================================================


def test_get_pending_friend_requests(client):
    user_1 = create_test_user(
        client,
        "Get Pending User One",
        "get_pending_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Get Pending User Two",
        "get_pending_user2@example.com",
    )

    # User 1 sends a request to User 2
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    # User 2 gets pending requests
    response = client.get(
        "/friend-requests/",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "pending"


def test_get_pending_friend_requests_returns_empty_list(client):
    user_1 = create_test_user(
        client,
        "Empty Pending User",
        "empty_pending_user@example.com",
    )

    response = client.get(
        "/friend-requests/",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data == []


# ============================================================
# ACCEPT FRIEND REQUEST
# ============================================================


def test_accept_friend_request_successfully(client):
    user_1 = create_test_user(
        client,
        "Accept User One",
        "accept_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Accept User Two",
        "accept_user2@example.com",
    )

    # User 1 sends request
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

    data = response.json()

    assert data["status"] == "accepted"


def test_sender_cannot_accept_friend_request(client):
    user_1 = create_test_user(
        client,
        "Sender Accept User",
        "sender_accept_user@example.com",
    )

    user_2 = create_test_user(
        client,
        "Receiver Accept User",
        "receiver_accept_user@example.com",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Sender tries to accept their own request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_accept_already_processed_friend_request(client):
    user_1 = create_test_user(
        client,
        "Processed Accept User One",
        "processed_accept_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Processed Accept User Two",
        "processed_accept_user2@example.com",
    )

    # Create request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Accept request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    # Try accepting again
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "This friend request has already been processed!"
    )


# ============================================================
# DECLINE FRIEND REQUEST
# ============================================================


def test_decline_friend_request_successfully(client):
    user_1 = create_test_user(
        client,
        "Decline User One",
        "decline_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Decline User Two",
        "decline_user2@example.com",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 2 declines
    response = client.patch(
        f"/friend-requests/{friend_request_id}/decline",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "declined"


def test_cannot_decline_already_processed_friend_request(client):
    user_1 = create_test_user(
        client,
        "Processed Decline User One",
        "processed_decline_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Processed Decline User Two",
        "processed_decline_user2@example.com",
    )

    # Create request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Decline request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/decline",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    # Try declining again
    response = client.patch(
        f"/friend-requests/{friend_request_id}/decline",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "This friend request has already been processed!"
    )


# ============================================================
# CANCEL FRIEND REQUEST
# ============================================================


def test_cancel_friend_request_successfully(client):
    user_1 = create_test_user(
        client,
        "Cancel User One",
        "cancel_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Cancel User Two",
        "cancel_user2@example.com",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 1 cancels request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/cancel",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "canceled"


def test_receiver_cannot_cancel_friend_request(client):
    user_1 = create_test_user(
        client,
        "Sender Cancel User",
        "sender_cancel_user@example.com",
    )

    user_2 = create_test_user(
        client,
        "Receiver Cancel User",
        "receiver_cancel_user@example.com",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 2 tries to cancel it
    response = client.patch(
        f"/friend-requests/{friend_request_id}/cancel",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_cancel_already_processed_friend_request(client):
    user_1 = create_test_user(
        client,
        "Processed Cancel User One",
        "processed_cancel_user1@example.com",
    )

    user_2 = create_test_user(
        client,
        "Processed Cancel User Two",
        "processed_cancel_user2@example.com",
    )

    # Create request
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": user_2["user_id"],
        },
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 2 accepts request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
        headers=user_2["headers"],
    )

    assert response.status_code == status.HTTP_200_OK

    # User 1 tries to cancel after acceptance
    response = client.patch(
        f"/friend-requests/{friend_request_id}/cancel",
        headers=user_1["headers"],
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "This friend request has already been processed!"
    )


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


def test_create_friend_request_without_authentication(client):
    response = client.post(
        "/friend-requests/create",
        json={
            "receiver_id": 1,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_friend_requests_without_authentication(client):
    response = client.get(
        "/friend-requests/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_accept_friend_request_without_authentication(client):
    response = client.patch(
        "/friend-requests/1/accept",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_decline_friend_request_without_authentication(client):
    response = client.patch(
        "/friend-requests/1/decline",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_cancel_friend_request_without_authentication(client):
    response = client.patch(
        "/friend-requests/1/cancel",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
