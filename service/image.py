from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from models.enums import ImageType


def get_image_path(image_type: ImageType):
    return Path(f"uploads/{image_type}s")


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def save_image(file: UploadFile, image_type: ImageType) -> str:
    # 1. Check the declared file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    # 2. Check the file size without reading the entire file
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be smaller than 5 MB.",
        )

    # 3. Validate that the file is actually an image
    try:
        image = Image.open(file.file)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file."
        )

    # 4. Reset the file position because Pillow has read from it
    file.file.seek(0)

    # 5. Generate a unique filename and save the image
    upload_dir = get_image_path(image_type)
    upload_dir.mkdir(parents=True, exist_ok=True)
    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    filename = f"{uuid4()}{extension}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return str(file_path)
