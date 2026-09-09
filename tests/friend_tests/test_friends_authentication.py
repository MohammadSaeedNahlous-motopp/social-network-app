from fastapi import status


# ============================================================
# AUTHENTICATION TESTS
# ============================================================


def test_get_friends_without_authentication(client):
    response = client.get("/friends/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_friend_without_authentication(client):
    response = client.delete("/friends/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
