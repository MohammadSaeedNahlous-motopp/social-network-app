from fastapi import UploadFile

from models.enums import ImageType
from service.image import save_image


async def save_post_image(file: UploadFile) -> str:
    """Validate and save an uploaded post image."""
    return await save_image(
        file=file,
        image_type=ImageType.post_picture,
    )


