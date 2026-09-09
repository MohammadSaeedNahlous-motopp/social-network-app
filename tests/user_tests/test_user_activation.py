from sqlalchemy.orm import Session


# ============================================================
# USER ACTIVATION TESTS
# ============================================================


def test_change_activation_to_inactive(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="activation_to_inactive@example.com",
        name="Activation Inactive User",
    )

    assert user.is_active is True

    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    db.refresh(user)

    assert user.is_active is False


def test_change_activation_to_active(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="activation_to_active@example.com",
        name="Activation Active User",
    )

    user.is_active = False

    db.commit()
    db.refresh(user)

    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    db.refresh(user)

    assert user.is_active is True


def test_change_activation_toggle(
    client,
    db: Session,
    authenticated_user,
):
    user = authenticated_user(
        email="activation_toggle_user@example.com",
        name="Activation Toggle User",
    )

    # True -> False
    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # False -> True
    response = client.patch("/users/toggle-active")

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    db.refresh(user)

    assert user.is_active is True


def test_change_activation_unauthorized(client):
    response = client.patch("/users/toggle-active")

    assert response.status_code == 401
