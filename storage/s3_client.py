import io
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from botocore.config import Config
from django.conf import settings
from minio.error import S3Error
from datetime import timedelta


class MinIOClient:
    def __init__(self):
        self.config = {
            "aws_access_key_id": settings.MINIO_STORAGE["ACCESS_KEY"],
            "aws_secret_access_key": settings.MINIO_STORAGE["SECRET_KEY"],
            "endpoint_url": settings.MINIO_STORAGE["ENDPOINT_URL"],
            "config": Config(signature_version="s3v4"),
        }
        self.bucket_name = settings.MINIO_STORAGE["BUCKET_NAME"]
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_name: str, file_data: bytes):
        async with self.get_client() as client:
            try:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_name,
                    Body=io.BytesIO(file_data),
                )
                return f"Файл {file_name} успешно загружен"
            except ClientError as e:
                return f"Ошибка: {e}"

    async def list_bucket_objects(self):
        async with self.get_client() as client:
            try:
                response = await client.list_objects_v2(Bucket=self.bucket_name)
                return [obj["Key"] for obj in response.get("Contents", [])]
            except ClientError as e:
                return f"Ошибка: {e}"




    async def get_presigned_url(self, object_name):
        """ Генерация ссылки на скачивание файла """
        async with self.get_client() as client:

            try:
                url = await client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": object_name},
                    ExpiresIn=3600,  # Время жизни ссылки (в секундах)
                )
                return url
            except ClientError as e:
                print(f"Ошибка: {e}")
                return None


    async def get_object_metadata(self, object_name):
        """ Получение метаданных файла (размер, владелец, дата загрузки) """
        async with self.get_client() as client:
            try:
                response = await client.head_object(
                    Bucket=self.bucket_name, Key=object_name
                )
                metadata = {
                    "Size": response.get("ContentLength"),
                    "LastModified": response.get("LastModified"),
                    "Owner": response.get("Owner", {}).get("DisplayName"),
                    "ETag": response.get("ETag"),
                    "Metadata": response.get("Metadata", {}),
                }
                return metadata
            except ClientError as e:
                return f"Ошибка: {e}"

    async def get_presigned_upload_url(self, filename):
        """Генерирует presigned URL для загрузки файла в MinIO"""
        async with self.get_client() as client:
            try:
                url = await client.generate_presigned_url(
                    "put_object",
                    Params={"Bucket": self.bucket_name, "Key": filename},
                    ExpiresIn=3600,  # Время жизни ссылки (в секундах)
                )
                return url
            except ClientError as e:
                return f"Ошибка MinIO: {str(e)}"

