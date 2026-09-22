import pytest
from fastapi import status
from sqlalchemy.orm import Session


def test_get_group_by_id(client, create_test_user, create_test_group):
    # Arrange
    user = create_test_user(
        email="get_group@example.com",
        name="John Doe",
    )

    group = create_test_group(
        owner=user,
        name="Python Developers",
        description="Python group",
    )

    # Act
    response = client.get(f"/groups/{group.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == group.id
    assert data["name"] == group.name
    assert data["description"] == group.description
    assert data["is_public"] is group.is_public
    assert data["owner"]["name"] == group.owner.name
    assert data["owner"]["email"] == group.owner.email


def test_get_group_by_id_not_found(client):
    # Arrange
    non_existing_group_id = 999999

    # Act
    response = client.get(f"/groups/{non_existing_group_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Group not found"


@pytest.mark.parametrize(
    "search_params, expected_names",
    [
        # test_search_groups_by_name
        (
            {"name": "python"},
            ["Python Developers", "Python Cooking Club"],
        ),
        # test_search_groups_case_insensitive
        (
            {"name": "PYTHON"},
            ["Python Developers", "Python Cooking Club"],
        ),
        # test_search_groups_matches_whole_search_string
        (
            {"name": "python developers"},
            ["Python Developers"],
        ),
        # search by description
        (
            {"description": "programming"},
            ["Python Developers", "Java Developers"],
        ),
        # search by both fields
        (
            {
                "name": "python",
                "description": "programming",
            },
            ["Python Developers"],
        ),
    ],
)
def test_search_groups(
    client,
    create_test_user,
    create_test_group,
    search_params,
    expected_names,
):
    user = create_test_user(email="search_test@example.com")

    groups = [
        ("Python Developers", "Programming group"),
        ("Java Developers", "Programming group"),
        ("Python Cooking Club", "Food enthusiasts"),
    ]

    for name, description in groups:
        create_test_group(
            owner=user,
            name=name,
            description=description,
        )

    response = client.get(
        "/groups/search",
        params=search_params,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == len(expected_names)
    assert [group["name"] for group in data["items"]] == expected_names


def test_search_groups_without_parameters(client):
    # Act
    response = client.get("/groups/search")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == (
        "At least one field must be provided for search"
    )


def test_search_groups_by_all_tags(
    client,
    db: Session,
    authenticated_user,
    create_test_group,
    add_test_tags,
):
    user = authenticated_user()

    group_1 = create_test_group(
        owner=user,
        name="Python and JavaScript",
    )
    add_test_tags(group_1, [1, 2])

    group_2 = create_test_group(
        owner=user,
        name="Python only",
    )
    add_test_tags(group_2, [1])

    group_3 = create_test_group(
        owner=user,
        name="JavaScript only",
    )
    add_test_tags(group_3, [2])

    response = client.get(
        "/groups/search",
        params={"tag_ids": "1,2"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python and JavaScript"


def test_search_groups_with_extra_tags(
    client,
    db: Session,
    authenticated_user,
    create_test_group,
    add_test_tags,
):
    user = authenticated_user()

    test_group = create_test_group(
        owner=user,
        name="Many Tags",
    )

    add_test_tags(test_group, [1, 2, 3, 5])

    response = client.get(
        "/groups/search",
        params={"tag_ids": "1,2"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Many Tags"

    assert {tag["id"] for tag in data["items"][0]["tags"]} == {1, 2, 3, 5}


def test_search_groups_excludes_groups_missing_tag(
    client,
    db: Session,
    authenticated_user,
    create_test_group,
    add_test_tags,
):
    user = authenticated_user()

    group_1 = create_test_group(
        owner=user,
        name="Has Both",
    )
    add_test_tags(group_1, [1, 2])

    group_2 = create_test_group(
        owner=user,
        name="Missing JavaScript",
    )
    add_test_tags(group_2, [1])

    response = client.get(
        "/groups/search",
        params={"tag_ids": "1,2"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Has Both"


def test_search_groups_by_name_and_tags(
    client,
    db: Session,
    authenticated_user,
    create_test_group,
    add_test_tags,
):
    user = authenticated_user()

    group_1 = create_test_group(
        owner=user,
        name="Python Backend",
    )
    add_test_tags(group_1, [1, 3])

    group_2 = create_test_group(
        owner=user,
        name="Python Frontend",
    )
    add_test_tags(group_2, [1, 4])

    group_3 = create_test_group(
        owner=user,
        name="JavaScript Backend",
    )
    add_test_tags(group_3, [2, 3])

    response = client.get(
        "/groups/search",
        params={
            "name": "Python",
            "tag_ids": "1,3",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python Backend"


def test_search_groups_by_single_tag(
    client,
    db: Session,
    authenticated_user,
    create_test_group,
    add_test_tags,
):
    user = authenticated_user()

    group_1 = create_test_group(
        owner=user,
        name="Python Group",
    )
    add_test_tags(group_1, [1])

    group_2 = create_test_group(
        owner=user,
        name="JavaScript Group",
    )
    add_test_tags(group_2, [2])

    response = client.get(
        "/groups/search",
        params={"tag_ids": "1"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python Group"


def test_search_groups_with_spaces_in_tag_ids(
    client,
    db: Session,
    authenticated_user,
    create_test_group,
    add_test_tags,
):
    user = authenticated_user()

    test_group = create_test_group(
        owner=user,
        name="Python JavaScript",
    )
    add_test_tags(test_group, [1, 2])

    response = client.get(
        "/groups/search",
        params={"tag_ids": "1, 2"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python JavaScript"
