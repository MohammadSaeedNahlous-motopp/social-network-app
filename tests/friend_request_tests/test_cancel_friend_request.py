from fastapi import status


def test_cancel_friend_request_successfully(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="cancel_user1@example.com",
        name="Cancel User One",
    )

    user_2 = create_test_user(
        email="cancel_user2@example.com",
        name="Cancel User Two",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # User 1 cancels
    response = client.delete(
        f"/friend-requests/{friend_request_id}/cancel",
    )

    assert response.status_code == status.HTTP_200_OK


def test_receiver_cannot_cancel_friend_request(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="sender_cancel_user@example.com",
        name="Sender Cancel User",
    )

    user_2 = create_test_user(
        email="receiver_cancel_user@example.com",
        name="Receiver Cancel User",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Switch to receiver
    authenticated_user(email=user_2.email)

    # Receiver tries to cancel
    response = client.delete(
        f"/friend-requests/{friend_request_id}/cancel",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_cannot_cancel_deleted_friend_request(
    client,
    create_test_user,
    authenticated_user,
):
    user_1 = authenticated_user(
        email="processed_cancel_user1@example.com",
        name="Processed Cancel User One",
    )

    user_2 = create_test_user(
        email="processed_cancel_user2@example.com",
        name="Processed Cancel User Two",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Switch to User 2 and accept
    authenticated_user(email=user_2.email)

    response = client.delete(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK

    # Switch back to User 1
    authenticated_user(email=user_1.email)

    # The request was deleted after acceptance,
    # so it cannot be cancelled anymore.
    response = client.delete(
        f"/friend-requests/{friend_request_id}/cancel",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == ("Friend request not found!")
