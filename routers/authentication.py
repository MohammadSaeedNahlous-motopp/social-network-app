from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import oauth2
from db.database import get_db
from db.hash import Hash
from models.enums import ImageType
from models.user import DBUser
from schemas.user import UserDisplay, UserBase
from db import user
from service.image import save_image


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user",
    description=(
        "Authenticates a user using their email address and password. "
        "The email address must be provided in the OAuth2 `username` field. "
        "When authentication is successful, the API returns a JWT access token "
        "that can be used to access protected endpoints."
    ),
    response_description="JWT access token and authenticated user information.",
    responses={
        200: {"description": "User authenticated successfully."},
        401: {"description": "Incorrect email or password."},
    },
)
def get_token(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return user.get_token(db, request)


@router.post(
    "/register",
    response_model=UserDisplay,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user account using the provided profile information. "
        "A profile image may optionally be uploaded together with the user's "
        "profile data. Supported profile image formats are JPG, PNG, and WEBP."
    ),
    response_description="The newly created user profile.",
    responses={
        201: {"description": "User account created successfully."},
        400: {
            "description": (
                "Invalid profile image or an account with the "
                "provided email address already exists."
            )
        },
    },
)
async def create_user(
    request: UserBase = Depends(UserBase.as_form),
    profile_img: UploadFile | None = File(
        None,
        description=(
            "Optional profile image. Supported formats: JPG, PNG, and WEBP. "
            "Maximum file size: 5 MB."
        ),
    ),
    db: Session = Depends(get_db),
):
    image_path = None

    if profile_img:
        image_path = await save_image(profile_img, ImageType.profile_picture)

    return user.register_user(request, db, image_path)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out the current user",
    description=(
        "Logs out the current user. The client should remove the stored "
        "JWT access token after receiving a successful response."
    ),
    response_description="Confirmation that the logout request was processed.",
    responses={200: {"description": "User logged out successfully."}},
)
def logout_user():
    return {"message": "Successfully logged out"}
