from fastapi import status


def test_get_pending_friend_requests(
    client,
    create_test_user,
    authenticated_user,
):
    authenticated_user(
        email="get_pending_user1@example.com",
        name="Get Pending User One",
    )

    user_2 = create_test_user(
        email="get_pending_user2@example.com",
        name="Get Pending User Two",
    )

    # User 1 sends request
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": user_2.id},
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Switch to User 2
    authenticated_user(email=user_2.email)

    # Get pending requests
    response = client.get("/friend-requests/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "pending"


def test_get_pending_friend_requests_returns_empty_list(
    client,
    authenticated_user,
):
    authenticated_user(
        email="empty_pending_user@example.com",
        name="Empty Pending User",
    )

    response = client.get("/friend-requests/")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []
