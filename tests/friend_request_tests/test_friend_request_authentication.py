from fastapi import status


def test_create_friend_request_without_authentication(client):
    response = client.post(
        "/friend-requests/create",
        json={"receiver_id": 1},
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
