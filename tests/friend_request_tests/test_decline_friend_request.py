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

    # User 2 declines
    response = client.delete(
        f"/friend-requests/{friend_request_id}/decline",
    )

    assert response.status_code == status.HTTP_200_OK


def test_cannot_decline_deleted_friend_request(
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

    # User 2 declines
    response = client.delete(
        f"/friend-requests/{friend_request_id}/decline",
    )

    assert response.status_code == status.HTTP_200_OK

    # Try declining the deleted request again
    response = client.delete(
        f"/friend-requests/{friend_request_id}/decline",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json()["detail"] == ("Friend request not found!")
