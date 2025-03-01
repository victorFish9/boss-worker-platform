import asyncio
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from django.conf import settings


class MinIOClient:
    def __init__(self):
        self.config = {
            "aws_access_key_id": settings.MINIO_STORAGE["ACCESS_KEY"],
            "aws_secret_access_key": settings.MINIO_STORAGE["SECRET_KEY"],
            "endpoint_url": settings.MINIO_STORAGE["ENDPOINT_URL"],
        }
        self.bucket_name = settings.MINIO_STORAGE["BUCKET_NAME"]
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_path: str):
        object_name = file_path.split("/")[-1]
        async with self.get_client() as client:
            try:
                with open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=file,
                    )
                return f"Файл {object_name} успешно загружен"
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
        async with self.session.create_client("s3", **self.config) as client:
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
