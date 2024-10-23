from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os

load_dotenv()

MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE'))


class ImageMetadata(BaseModel):
    filename: str
    content_type: str
    size_bytes: int = Field(lt=MAX_IMAGE_SIZE)
    original_type: str = Field(description="Original detected image format")

    class Config:
        json_schema_extra = {
            'example': {
                'filename': 'thumbnail.jpg',
                'content_type': 'image/jpeg',
                'size_bytes': 1048576,
                'original_type': 'jpg'
            }
        }


class ImageResponse(ImageMetadata):
    id: str
    access_url: str

    class Config:
        json_schema_extra = {
            'example': {
                'id': '550e8400-e29b-41d4-a716-446655440000',
                'filename': 'thumbnail.jpg',
                'content_type': 'image/jpeg',
                'size_bytes': 1048576,
                'original_type': 'jpg',
                'access_url': 'https://example.com/550e8400-e29b-41d4-a716-446655440000.jpg'
            }
        }
