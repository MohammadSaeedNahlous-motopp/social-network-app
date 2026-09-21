from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
)
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import post as db_post
from db.database import get_db
from models.user import DBUser
from schemas.post import PostCreate, PostUpdate, PostResponse
from service.image import save_image
from models.enums import ImageType, PostVisibility
from service.pagination import PaginatedResponse, calculate_total_pages, paginate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    description=(
        "Creates a new post for the currently authenticated user. "
        "The post must contain a title and content and may optionally include an image. "
        "The uploaded image must be a valid JPG, PNG, or WEBP image and must not "
        "exceed the maximum allowed file size."
    ),
    response_description="The newly created post.",
    responses={
        201: {"description": "Post created successfully."},
        400: {"description": "The uploaded image is invalid."},
        401: {"description": "Authentication is required to create a post."},
    },
)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    visibility: PostVisibility = Form(PostVisibility.public),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Create a post for the currently authenticated user."""

    image_url = None

    if image is not None:
        image_url = await save_image(image, ImageType.post_picture)

    request = PostCreate(
        title=title,
        content=content,
        visibility=visibility

    )

    result = db_post.create_post(
        db=db,
        request=request,
        user_id=current_user.id,
        image_url=image_url,
    )
    return result

@router.get(
    "/feed",
    response_model=PaginatedResponse[PostResponse],
    status_code=status.HTTP_200_OK,
    summary="View personal feed",
    description=(
        "Retrieves posts for the authenticated user's feed. "
        "The feed contains the user's own posts, posts from friends, "
        "and posts from groups the user belongs to."
    ),
    response_description="The authenticated user's paginated feed.",
    responses={
        200: {"description": "Feed retrieved successfully."},
        401: {"description": "Authentication is required to view the feed."},
    },
)
def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Return the authenticated user's paginated feed."""

    query = db_post.get_feed(
        db=db,
        user_id=current_user.id,
    )

    total = query.count()

    paginated_query = paginate(
        query=query,
        page=page,
        page_size=page_size,
    )

    items = paginated_query.all()

    result_feed = {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": calculate_total_pages(
            total=total,
            page_size=page_size,
        ),
    }
    return result_feed


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a post",
    description=(
        "Retrieves a visible post using its ID. "
        "If the post does not exist or is not visible, a 404 response is returned."
    ),
    response_description="The requested post.",
    responses={
        200: {"description": "Post retrieved successfully."},
        404: {"description": "Post not found."},
    },
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Retrieve a visible post by its ID."""

    post = db_post.get_post(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    return post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a post",
    description=(
        "Updates the title or content of a post owned by the currently "
        "authenticated user. The image cannot be changed or removed after "
        "the post has been published."
    ),
    response_description="The updated post.",
    responses={
        200: {"description": "Post updated successfully."},
        401: {"description": "Authentication is required to update a post."},
        404: {
            "description": (
                "The post was not found or does not belong to the authenticated user."
            )
        },
    },
)
def update_post(
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Update the title or content of a post owned by the current user."""

    post = db_post.update_post(
        db=db,
        post_id=post_id,
        request=request,
        user_id=current_user.id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    return post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a post",
    description=(
        "Deletes a post owned by the currently authenticated user. "
        "The post is permanently removed from the database."
    ),
    response_description="Confirmation that the post was deleted.",
    responses={
        200: {"description": "Post deleted successfully."},
        401: {"description": "Authentication is required to delete a post."},
        404: {
            "description": (
                "The post was not found or does not belong to the authenticated user."
            )
        },
    },
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Delete a post owned by the currently authenticated user."""

    post = db_post.delete_post(
        db=db,
        post_id=post_id,
        user_id=current_user.id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    message = {"message": "Post deleted successfully."}
    return message


@router.get(
    "/{user_id}/all",
    response_model=PaginatedResponse[PostResponse],
    status_code=status.HTTP_200_OK,
    summary="View a user's personal wall",
    description=(
        "Retrieves the published posts of a specific user. "
        "The personal wall contains only posts created by that user."
    ),
    response_description="The user's published posts.",
    responses={
        200: {"description": "User posts retrieved successfully."},
    },
)
def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """Return paginated posts belonging to a specific user."""

    query = db_post.get_posts_by_user(
        db=db,
        user_id=user_id,
        current_user_id=current_user.id
    )

    total = query.count()

    paginated_query = paginate(
        query=query,
        page=page,
        page_size=page_size,
    )

    items = paginated_query.all()

    result = {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": calculate_total_pages(
            total=total,
            page_size=page_size,
        ),
    }
    return result
