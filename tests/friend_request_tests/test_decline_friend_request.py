from fastapi import status


def test_decline_friend_request_successfully(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="decline_user1@example.com",
        name="Decline User One",
    )

    user_2 = create_test_user(
        email="decline_user2@example.com",
        name="Decline User Two",
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

    # Decline
    response = client.patch(
        f"/friend-requests/{friend_request_id}/decline",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["status"] == "declined"


def test_cannot_decline_already_processed_friend_request(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="processed_decline_user1@example.com",
        name="Processed Decline User One",
    )

    user_2 = create_test_user(
        email="processed_decline_user2@example.com",
        name="Processed Decline User Two",
    )

    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    friend_request_id = response.json()["id"]

    # Switch to User 2
    authenticated_user(email=user_2.email)

    # Decline
    response = client.patch(
        f"/friend-requests/{friend_request_id}/decline",
    )

    assert response.status_code == status.HTTP_200_OK

    # Try declining again
    response = client.patch(
        f"/friend-requests/{friend_request_id}/decline",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json()["detail"] == (
        "This friend request has already been processed!"
    )
