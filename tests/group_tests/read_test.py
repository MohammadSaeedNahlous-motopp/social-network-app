import pytest
from fastapi import status

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

    assert len(data) == len(expected_names)
    assert [group["name"] for group in data] == expected_names


def test_search_groups_without_parameters(client):
    # Act
    response = client.get("/groups/search")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == (
        "At least one field must be provided for search"
    )