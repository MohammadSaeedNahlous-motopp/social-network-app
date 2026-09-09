from fastapi import status


# ============================================================
# GET FRIENDS
# ============================================================


def test_get_friends_successfully(
    client,
    create_test_user,
    authenticated_user,
):
    user_1 = create_test_user(
        email="friends_list_user_one@example.com",
        name="Friends List User One",
    )

    user_2 = create_test_user(
        email="friends_list_user_two@example.com",
        name="Friends List User Two",
    )

    # Authenticate as User 1
    authenticated_user(
        email=user_1.email,
        name=user_1.name,
    )

    # User 1 sends a friend request to User 2
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

    # User 2 accepts the friend request
    response = client.patch(
        f"/friend-requests/{friend_request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK

    # Authenticate as User 1 again
    authenticated_user(
        email=user_1.email,
        name=user_1.name,
    )

    # User 1 gets friends
    response = client.get("/friends/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["friend"]["id"] == user_2.id
    assert data[0]["friend"]["name"] == user_2.name


def test_get_friends_returns_empty_list(
    client,
    authenticated_user,
):
    authenticated_user(
        email="no_friends_user@example.com",
        name="No Friends User",
    )

    response = client.get("/friends/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
