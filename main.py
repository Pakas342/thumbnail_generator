from fastapi import FastAPI, UploadFile, HTTPException
from dotenv import load_dotenv
import os
import filetype
import uuid
import uvicorn
from typing import Optional
from models import ImageMetadata, ImageResponse


class ImageValidationError(Exception):
    """Custom exception for image validation errors"""
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


load_dotenv()

MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10*1024*1024))
ALLOWED_IMAGE_TYPES = {'jpeg', 'png', 'gif', 'bmp', 'webp', 'jpg'}

app = FastAPI(title='thumbnail_generator', version='1.0.0')


async def validate_image(file: UploadFile) -> ImageMetadata:
    """Validates image type and size"""
    content = await file.read()
    await file.seek(0)
    if len(content) > MAX_IMAGE_SIZE:
        raise ImageValidationError(f"File size exceeds maximum allowed size of {MAX_IMAGE_SIZE / 1024 / 1024}MB")

    file_type = filetype.guess(content)
    if not file_type:
        raise ImageValidationError("File does not appear to be a valid image")

    extension = file_type.extension
    if extension not in ALLOWED_IMAGE_TYPES:
        raise ImageValidationError(
            f"Image type {extension} not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}")

    return ImageMetadata(
        filename=file.filename,
        content_type=file_type.mime,
        size_bytes=len(content),
        original_type=extension
    )


@app.post("/image/",
          response_model=ImageResponse,
          summary="transform an image into a thumbnail",
          description=f"Upload an image file (max {MAX_IMAGE_SIZE / 1024 / 1024}MB) of types: "
                      f"{', '.join(ALLOWED_IMAGE_TYPES)}")
async def upload_image(file: UploadFile) -> ImageResponse:
    try:
        metadata = await validate_image(file)
        image_id = str(uuid.uuid4())
        return ImageResponse(
            filename=metadata.filename,
            content_type=metadata.content_type,
            size_bytes=metadata.size_bytes,
            original_type=metadata.original_type,
            id=image_id,
            access_url=f'https://example.com/{image_id}.{metadata.original_type}'
        )

    except ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
