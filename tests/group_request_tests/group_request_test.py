from fastapi import status

from models.enums import GroupRole, RequestStatus
from models.group_member import DBGroupMember
from models.group_request import DBGroupRequest


# ============================================================
# CREATE GROUP REQUEST
# ============================================================


def test_create_group_request(
    client,
    authenticated_user,
    create_test_group,
):
    user = authenticated_user()

    group = create_test_group(
        owner=user,
        is_public=False,
    )

    response = client.post(
        "/group-requests/create",
        json={
            "group_id": group.id,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["group"]["id"] == group.id
    assert data["group"]["name"] == group.name

    assert data["sender"]["id"] == user.id
    assert data["sender"]["name"] == user.name

    assert data["status"] == RequestStatus.pending.value


def test_create_group_request_public_group(
    client,
    authenticated_user,
    create_test_group,
):
    user = authenticated_user()

    group = create_test_group(
        owner=user,
        is_public=True,
    )

    response = client.post(
        "/group-requests/create",
        json={
            "group_id": group.id,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found!"


def test_create_group_request_group_not_found(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.post(
        "/group-requests/create",
        json={
            "group_id": 999999,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found!"


def test_create_duplicate_pending_group_request(
    client,
    authenticated_user,
    create_test_group,
):
    user = authenticated_user()

    group = create_test_group(
        owner=user,
        is_public=False,
    )

    first_response = client.post(
        "/group-requests/create",
        json={
            "group_id": group.id,
        },
    )

    assert first_response.status_code == status.HTTP_201_CREATED

    second_response = client.post(
        "/group-requests/create",
        json={
            "group_id": group.id,
        },
    )

    assert second_response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        second_response.json()["detail"]
        == "A pending group joining request already exists!"
    )


def test_create_group_request_already_member(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    user = authenticated_user()

    group = create_test_group(
        owner=user,
        is_public=False,
    )

    member_role = get_test_group_role(GroupRole.member)

    create_test_group_member(
        group=group,
        user=user,
        role=member_role,
    )

    response = client.post(
        "/group-requests/create",
        json={
            "group_id": group.id,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "You can not send group joining request to already joined group"
    )


def test_create_group_request_unauthenticated(
    client,
    create_test_group,
    create_test_user,
):
    user = create_test_user()

    group = create_test_group(
        owner=user,
        is_public=False,
    )

    response = client.post(
        "/group-requests/create",
        json={
            "group_id": group.id,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_group_request_invalid_body(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.post(
        "/group-requests/create",
        json={},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================
# GET PENDING GROUP REQUESTS
# ============================================================


def test_get_pending_group_requests(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    admin = authenticated_user(
        email="admin@example.com",
        name="Admin",
    )

    requester = create_test_user(
        email="requester@example.com",
        name="Requester",
    )

    group = create_test_group(
        owner=admin,
        is_public=False,
    )

    admin_role = get_test_group_role(GroupRole.administrator)

    create_test_group_member(
        group=group,
        user=admin,
        role=admin_role,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    response = client.get(
        f"/group-requests/?group_id={group.id}",
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1

    assert data["items"][0]["id"] == group_request.id

    assert data["items"][0]["group"]["id"] == group.id
    assert data["items"][0]["group"]["name"] == group.name

    assert data["items"][0]["sender"]["id"] == requester.id
    assert data["items"][0]["sender"]["name"] == requester.name

    assert data["items"][0]["status"] == RequestStatus.pending.value


def test_get_pending_group_requests_forbidden_for_non_admin(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
):
    user = authenticated_user()

    group = create_test_group(
        owner=user,
        is_public=False,
    )

    member_role = get_test_group_role(GroupRole.member)

    create_test_group_member(
        group=group,
        user=user,
        role=member_role,
    )

    response = client.get(
        f"/group-requests/?group_id={group.id}",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_pending_group_requests_unauthenticated(
    client,
):
    response = client.get(
        "/group-requests/?group_id=1",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# ACCEPT GROUP REQUEST
# ============================================================
def test_accept_group_request(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    admin = authenticated_user(
        email="admin@example.com",
        name="Admin",
    )

    requester = create_test_user(
        email="requester@example.com",
        name="Requester",
    )

    group = create_test_group(
        owner=admin,
        is_public=False,
    )

    admin_role = get_test_group_role(
        GroupRole.administrator,
    )

    create_test_group_member(
        group=group,
        user=admin,
        role=admin_role,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    request_id = group_request.id

    response = client.delete(
        f"/group-requests/{request_id}/accept",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is True

    # Request should be deleted
    deleted_request = (
        db.query(DBGroupRequest).filter(DBGroupRequest.id == request_id).first()
    )

    assert deleted_request is None

    # Requester should now be a group member
    membership = (
        db.query(DBGroupMember)
        .filter(
            DBGroupMember.user_id == requester.id,
            DBGroupMember.group_id == group.id,
        )
        .first()
    )

    assert membership is not None

    # New member should have the member role
    member_role = get_test_group_role(
        GroupRole.member,
    )

    assert membership.role_id == member_role.id


def test_accept_group_request_forbidden_for_non_admin(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    admin = create_test_user(
        email="admin@example.com",
        name="Admin",
    )

    requester = authenticated_user(
        email="requester@example.com",
        name="Requester",
    )

    group = create_test_group(
        owner=admin,
        is_public=False,
    )

    admin_role = get_test_group_role(GroupRole.administrator)

    create_test_group_member(
        group=group,
        user=admin,
        role=admin_role,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    response = client.delete(
        f"/group-requests/{group_request.id}/accept",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_sender_cannot_accept_group_request(
    client,
    authenticated_user,
    create_test_group,
    db,
):
    requester = authenticated_user()

    group = create_test_group(
        owner=requester,
        is_public=False,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    response = client.delete(
        f"/group-requests/{group_request.id}/accept",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_accept_group_request_not_found(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.delete(
        "/group-requests/999999/accept",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_accept_already_processed_group_request(
    client,
    authenticated_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    admin = authenticated_user()

    group = create_test_group(
        owner=admin,
        is_public=False,
    )

    admin_role = get_test_group_role(GroupRole.administrator)

    create_test_group_member(
        group=group,
        user=admin,
        role=admin_role,
    )

    group_request = DBGroupRequest(
        sender_id=admin.id,
        group_id=group.id,
        status=RequestStatus.accepted,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    response = client.delete(
        f"/group-requests/{group_request.id}/accept",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "This group request has already been processed!"


# ============================================================
# DECLINE GROUP REQUEST
# ============================================================


def test_decline_group_request(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    admin = authenticated_user(
        email="admin@example.com",
        name="Admin",
    )

    requester = create_test_user(
        email="requester@example.com",
        name="Requester",
    )

    group = create_test_group(
        owner=admin,
        is_public=False,
    )

    admin_role = get_test_group_role(GroupRole.administrator)

    create_test_group_member(
        group=group,
        user=admin,
        role=admin_role,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    request_id = group_request.id

    response = client.delete(
        f"/group-requests/{request_id}/decline",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is True

    deleted_request = (
        db.query(DBGroupRequest).filter(DBGroupRequest.id == request_id).first()
    )

    assert deleted_request is None


def test_decline_group_request_forbidden_for_non_admin(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    create_test_group_member,
    get_test_group_role,
    db,
):
    admin = create_test_user(
        email="admin@example.com",
        name="Admin",
    )

    requester = authenticated_user(
        email="requester@example.com",
        name="Requester",
    )

    group = create_test_group(
        owner=admin,
        is_public=False,
    )

    admin_role = get_test_group_role(GroupRole.administrator)

    create_test_group_member(
        group=group,
        user=admin,
        role=admin_role,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    response = client.delete(
        f"/group-requests/{group_request.id}/decline",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_decline_group_request_not_found(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.delete(
        "/group-requests/999999/decline",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================
# CANCEL GROUP REQUEST
# ============================================================


def test_cancel_group_request(
    client,
    authenticated_user,
    create_test_group,
    db,
):
    requester = authenticated_user()

    group = create_test_group(
        owner=requester,
        is_public=False,
    )

    group_request = DBGroupRequest(
        sender_id=requester.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    request_id = group_request.id

    response = client.delete(
        f"/group-requests/{request_id}/cancel",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is True

    deleted_request = (
        db.query(DBGroupRequest).filter(DBGroupRequest.id == request_id).first()
    )

    assert deleted_request is None


def test_cancel_group_request_forbidden_for_non_sender(
    client,
    authenticated_user,
    create_test_user,
    create_test_group,
    db,
):
    sender = create_test_user(
        email="sender@example.com",
        name="Sender",
    )

    authenticated_user(
        email="other@example.com",
        name="Other",
    )

    group = create_test_group(
        owner=sender,
        is_public=False,
    )

    group_request = DBGroupRequest(
        sender_id=sender.id,
        group_id=group.id,
        status=RequestStatus.pending,
    )

    db.add(group_request)
    db.commit()
    db.refresh(group_request)

    response = client.delete(
        f"/group-requests/{group_request.id}/cancel",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_cancel_group_request_not_found(
    client,
    authenticated_user,
):
    authenticated_user()

    response = client.delete(
        "/group-requests/999999/cancel",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
