from fastapi import UploadFile
import boto3
from botocore.exceptions import ClientError
import logging
from app.core.config import get_settings
from uuid import UUID

settings = get_settings()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, user_id: UUID) -> str:
        """Upload a file to S3 and return the file path"""
        try:
            # Create a unique file path
            file_path = f"documents/{user_id}/{file.filename}"
            
            # Upload the file
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_path,
                ExtraArgs={
                    "ContentType": file.content_type
                }
            )
            
            return f"s3://{self.bucket_name}/{file_path}"
        
        except ClientError as e:
            logging.error(f"Error uploading file to S3: {e}")
            raise Exception("Failed to upload file to storage")

    async def delete_file(self, file_path: str):
        """Delete a file from S3"""
        try:
            # Extract the key from the full s3 path
            key = file_path.replace(f"s3://{self.bucket_name}/", "")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
        except ClientError as e:
            logging.error(f"Error deleting file from S3: {e}")
            raise Exception("Failed to delete file from storage") 