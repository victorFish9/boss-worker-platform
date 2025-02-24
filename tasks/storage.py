import os
import boto3

AWS_ACCESS_KEY_ID = os.getenv("MINIO_ACCESS_KEY", "admin")
AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_SECRET_KEY", "password")
AWS_STORAGE_BUCKET_NAME = "bossworker"
ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def generate_presigned_url(file_key, expiration=3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": AWS_STORAGE_BUCKET_NAME, "Key": file_key},
        ExpiresIn = expiration,
    )