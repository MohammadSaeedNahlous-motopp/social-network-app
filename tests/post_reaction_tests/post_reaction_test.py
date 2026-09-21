from models.enums import PostReactionType
from models.post import DBPost
from models.post_reactions import DBPostReaction


class TestCreatePostReaction:
    def test_create_like_reaction(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.like.value,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["post_id"] == post.id
        assert data["user_id"] == user.id
        assert data["reaction_type"] == PostReactionType.like.value

        db.refresh(post)

        assert post.score == 1

    def test_create_dislike_reaction(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.dislike.value,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["post_id"] == post.id
        assert data["user_id"] == user.id
        assert data["reaction_type"] == PostReactionType.dislike.value

        db.refresh(post)

        assert post.score == -1


class TestChangePostReaction:
    def test_change_like_to_dislike(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        # Create like
        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.like.value,
            },
        )

        assert response.status_code == 200

        db.refresh(post)

        assert post.score == 1

        # Change like to dislike
        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.dislike.value,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["post_id"] == post.id
        assert data["user_id"] == user.id
        assert data["reaction_type"] == PostReactionType.dislike.value

        db.refresh(post)

        assert post.score == -1

        reaction = (
            db.query(DBPostReaction)
            .filter(
                DBPostReaction.post_id == post.id,
                DBPostReaction.user_id == user.id,
            )
            .first()
        )

        assert reaction is not None
        assert reaction.reaction_type == PostReactionType.dislike


class TestRemovePostReaction:
    def test_remove_like(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        # Create like
        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.like.value,
            },
        )

        assert response.status_code == 200

        db.refresh(post)

        assert post.score == 1

        # Send the same reaction again -> remove it
        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.like.value,
            },
        )

        assert response.status_code == 200
        assert response.json() is True

        db.refresh(post)

        assert post.score == 0

        reaction = (
            db.query(DBPostReaction)
            .filter(
                DBPostReaction.post_id == post.id,
                DBPostReaction.user_id == user.id,
            )
            .first()
        )

        assert reaction is None

    def test_remove_dislike(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        # Create dislike
        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.dislike.value,
            },
        )

        assert response.status_code == 200

        db.refresh(post)

        assert post.score == -1

        # Send the same reaction again -> remove it
        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.dislike.value,
            },
        )

        assert response.status_code == 200
        assert response.json() is True

        db.refresh(post)

        assert post.score == 0

        reaction = (
            db.query(DBPostReaction)
            .filter(
                DBPostReaction.post_id == post.id,
                DBPostReaction.user_id == user.id,
            )
            .first()
        )

        assert reaction is None


class TestGetPostReactions:
    def test_get_post_reactions(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        reaction = DBPostReaction(
            post_id=post.id,
            user_id=user.id,
            reaction_type=PostReactionType.like,
        )

        db.add(reaction)
        db.commit()
        db.refresh(reaction)

        response = client.get(f"/posts/{post.id}/reactions")

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 1
        assert data["total_pages"] == 1

        assert len(data["items"]) == 1

        item = data["items"][0]

        assert item["id"] == reaction.id
        assert item["post_id"] == post.id
        assert item["user_id"] == user.id
        assert item["reaction_type"] == PostReactionType.like.value

    def test_get_post_reactions_empty(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.get(f"/posts/{post.id}/reactions")

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 0
        assert data["total_pages"] == 0
        assert data["items"] == []

    def test_get_post_reactions_with_pagination(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        reaction = DBPostReaction(
            post_id=post.id,
            user_id=user.id,
            reaction_type=PostReactionType.like,
        )

        db.add(reaction)
        db.commit()
        db.refresh(reaction)

        response = client.get(f"/posts/{post.id}/reactions?page=1&page_size=10")

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 1
        assert data["total_pages"] == 1
        assert len(data["items"]) == 1

    def test_get_post_reactions_second_page(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        reaction = DBPostReaction(
            post_id=post.id,
            user_id=user.id,
            reaction_type=PostReactionType.like,
        )

        db.add(reaction)
        db.commit()

        response = client.get(f"/posts/{post.id}/reactions?page=2&page_size=10")

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 1
        assert data["total_pages"] == 1
        assert data["items"] == []

    def test_get_post_reactions_invalid_page(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.get(f"/posts/{post.id}/reactions?page=0")

        assert response.status_code == 422

    def test_get_post_reactions_invalid_page_size(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.get(f"/posts/{post.id}/reactions?page_size=101")

        assert response.status_code == 422


class TestPostReactionValidation:
    def test_react_to_non_existing_post(
        self,
        client,
        authenticated_user,
    ):
        authenticated_user()

        response = client.post(
            "/posts/999999/reactions",
            json={
                "reaction_type": PostReactionType.like.value,
            },
        )

        assert response.status_code == 404

    def test_get_reactions_for_non_existing_post(
        self,
        client,
        authenticated_user,
    ):
        authenticated_user()

        response = client.get("/posts/999999/reactions")

        assert response.status_code == 404

    def test_invalid_reaction_type(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": "invalid_reaction",
            },
        )

        assert response.status_code == 422

    def test_missing_reaction_type(
        self,
        client,
        db,
        authenticated_user,
    ):
        user = authenticated_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        response = client.post(
            f"/posts/{post.id}/reactions",
            json={},
        )

        assert response.status_code == 422


class TestPostReactionAuthentication:
    def test_create_reaction_unauthenticated(
        self,
        client,
        db,
        create_test_user,
    ):
        user = create_test_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        from auth.oauth2 import get_current_user
        from main import app

        app.dependency_overrides.pop(
            get_current_user,
            None,
        )

        response = client.post(
            f"/posts/{post.id}/reactions",
            json={
                "reaction_type": PostReactionType.like.value,
            },
        )

        assert response.status_code == 401

    def test_get_reactions_unauthenticated(
        self,
        client,
        db,
        create_test_user,
    ):
        user = create_test_user()

        post = DBPost(
            user_id=user.id,
            title="Test post",
            content="Test content",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        from auth.oauth2 import get_current_user
        from main import app

        app.dependency_overrides.pop(
            get_current_user,
            None,
        )

        response = client.get(f"/posts/{post.id}/reactions")

        assert response.status_code == 401
