import boto3
from src.core.config import settings
s3 = boto3.client(
    "s3",
    endpoint_url=settings.OBJECT_STORAGE_ENDPOINT,
    aws_access_key_id=settings.OBJECT_STORAGE_ACCESS_KEY,
    aws_secret_access_key=settings.OBJECT_STORAGE_SECRET_KEY,
    region_name=settings.OBJECT_STORAGE_REGION,
)

async def upload_file_to_storage(file_key: str, file_content: bytes) -> str:
    s3.upload_fileobj(
        Fileobj=file_content,
        Bucket=settings.OBJECT_STORAGE_BUCKET_NAME,
        Key=file_key,
    )
    return file_key

def url_generate(file_key: str) -> str:
    if settings.OBJECT_STORAGE_CUSTOM_DOMAIN:
        return f"{settings.OBJECT_STORAGE_CUSTOM_DOMAIN}/{file_key}"
    else:
        return f"{settings.OBJECT_STORAGE_ENDPOINT}/{settings.OBJECT_STORAGE_BUCKET_NAME}/{file_key}"
    
