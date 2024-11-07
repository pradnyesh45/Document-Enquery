import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        logger.info(f"Initializing S3 client with bucket: {settings.S3_BUCKET_NAME}")
        logger.info(f"AWS Region: {settings.AWS_REGION}")
        logger.info(f"AWS Access Key ID: {settings.AWS_ACCESS_KEY_ID[:4]}...")  # Log only first 4 chars
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file_data, file_name: str) -> str:
        """Upload a file to S3"""
        try:
            logger.info(f"Attempting to upload file: {file_name}")
            
            # Upload the file
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                file_name
            )
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
            logger.info(f"Successfully uploaded file. URL: {url}")
            return url
            
        except ClientError as e:
            error_msg = f"Error uploading file to S3: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to storage: {str(e)}"
            )

    async def get_file(self, file_name: str):
        """Get a file from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return response['Body']
        except ClientError as e:
            logger.error(f"Error getting file from S3: {e}")
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )

    async def delete_file(self, file_name: str) -> bool:
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete file from storage"
            )