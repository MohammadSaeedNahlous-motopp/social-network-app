from fastapi import status


def test_accept_friend_request_successfully(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="accept_user1@example.com",
        name="Accept User One",
    )

    user_2 = create_test_user(
        email="accept_user2@example.com",
        name="Accept User Two",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Switch to User 2
    authenticated_user(email=user_2.email)

    # User 2 accepts
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["status"] == "accepted"


def test_sender_cannot_accept_friend_request(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="sender_accept_user@example.com",
        name="Sender Accept User",
    )

    user_2 = create_test_user(
        email="receiver_accept_user@example.com",
        name="Receiver Accept User",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Sender tries to accept their own request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_accept_already_processed_friend_request(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="processed_accept_user1@example.com",
        name="Processed Accept User One",
    )

    user_2 = create_test_user(
        email="processed_accept_user2@example.com",
        name="Processed Accept User Two",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Switch to User 2 and accept
    authenticated_user(email=user_2.email)

    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK

    # Try accepting again
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "This friend request has already been processed!"
    )
