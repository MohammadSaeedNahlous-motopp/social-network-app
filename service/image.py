from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError


UPLOAD_DIR = Path("uploads/profile_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def save_profile_image(file: UploadFile) -> str:
    # 1. Check the declared file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    # 2. Read the uploaded file
    file_data = await file.read()

    # 3. Check file size
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile image must be smaller than 5 MB.",
        )

    # 4. Verify that the file is actually a valid image
    try:
        image = Image.open(BytesIO(file_data))
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file."
        )

    # 5. Generate a unique filename
    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    filename = f"{uuid4()}{extension}"

    # 6. Create the file path
    file_path = UPLOAD_DIR / filename

    # 7. Save the image
    with open(file_path, "wb") as buffer:
        buffer.write(file_data)

    # 8. Return the path that will be stored in the database
    return str(file_path)
