import boto3
import logging
from io import BytesIO
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class S3UploadService:
    """
    Service for uploading files to s3

    Automatically uses environment credentials
    """
    def __init__(self, bucket_name: str, region_name: str):
        
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region_name)

    async def uploadFile(
            self,
            content: str,
            s3_key: str,
            content_type: str,
            metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            file_obj = BytesIO(content.encode('utf-8'))
            extra_args = {'ContentType': content_type}

            if metadata:
                extra_args['Metadata'] = metadata

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            return True

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to upload ({s3_key}): {e}")
            raise 