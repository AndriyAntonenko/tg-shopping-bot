import aioboto3
from botocore.exceptions import ClientError

from ..config import settings


class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket = settings.do_bucket
        self.region = settings.do_region
        self.config = {
            "region_name": settings.do_region,
            "endpoint_url": settings.do_endpoint,
            "aws_access_key_id": settings.do_key,
            "aws_secret_access_key": settings.do_secret,
        }

    async def upload_file(self, file_content, file_name, content_type):
        try:
            async with self.session.client("s3", **self.config) as client:
                await client.put_object(
                    Bucket=self.bucket,
                    Key=file_name,
                    Body=file_content,
                    ACL="public-read",
                    ContentType=content_type,
                )

            url = f"https://{self.bucket}.{self.region}.cdn.digitaloceanspaces.com/{self.bucket}/{file_name}"
            return url
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return None

    async def delete_file(self, file_name):
        try:
            async with self.session.client("s3", **self.config) as client:
                await client.delete_object(Bucket=self.bucket, Key=file_name)
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False
