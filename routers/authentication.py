from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import oauth2
from db.database import get_db
from models.enums import ImageType
from models.user import DBUser
from schemas.session import (
    TokenResponse,
    GetTokenResponse,
    RefreshTokenRequest,
    MessageResponse,
)
from schemas.user import UserDisplay, UserBase
from db import user, session
from service.image import save_image


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user",
    response_model=GetTokenResponse,
    description=(
        "Authenticates a user using their email address and password. "
        "The email address must be provided in the OAuth2 `username` field. "
        "When authentication is successful, the API creates a server-side "
        "session and returns a short-lived session token and a long-lived "
        "refresh token."
    ),
    response_description=(
        "Session token, refresh token, and authenticated user information."
    ),
    responses={
        200: {"description": "User authenticated successfully."},
        401: {"description": "Incorrect email or password."},
    },
)
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return user.login(db, request)


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
        image_path = await save_image(
            profile_img,
            ImageType.profile_picture,
        )

    return user.register_user(request, db, image_path)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh the session token",
    response_model=TokenResponse,
    description=(
        "Generates a new short-lived session token using a valid refresh token. "
        "The existing refresh token remains valid until it expires or the "
        "associated session is revoked."
    ),
    response_description="A new session token and the existing refresh token.",
    responses={
        200: {"description": "Session token refreshed successfully."},
        403: {
            "description": "Refresh token is expired or the session has been revoked."
        },
        404: {
            "description": "Session associated with the refresh token was not found."
        },
    },
)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    _, access_token, refresh_token = session.refresh_session(
        request.refresh_token,
        db,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.patch(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Log out of the current session",
    description=(
        "Revokes the session associated with the provided session token. "
        "Only the current session is revoked; other active sessions remain valid. "
        "The client should remove the session token and refresh token after "
        "a successful logout."
    ),
    response_description="Confirmation that the current session was revoked.",
    responses={
        200: {"description": "Current session logged out successfully."},
        404: {"description": "Session not found."},
        403: {"description": "Session has already been revoked."},
    },
)
def logout_user(
    access_token: str = Depends(oauth2.oauth2_schema),
    db: Session = Depends(get_db),
):
    session.revoke_session(access_token, db)

    return {"message": "Logged out successfully."}


@router.patch(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Log out of all sessions",
    description=(
        "Revokes all active sessions belonging to the authenticated user. "
        "This logs the user out from all devices and active sessions. "
        "The client should remove the stored session token and refresh token "
        "after a successful logout."
    ),
    response_description="Confirmation that all user sessions were revoked.",
    responses={
        200: {"description": "All user sessions logged out successfully."},
        404: {"description": "Authenticated user was not found."},
    },
)
def logout_all(
    current_user: DBUser = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    session.revoke_all_sessions(current_user.id, db)

    return {"message": "Logged out successfully from all sessions."}
