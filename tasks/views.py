from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .storage import s3_client, AWS_STORAGE_BUCKET_NAME

@csrf_exempt
def upload_to_minio(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_name = uploaded_file.name

        try:
            # Загружаем файл в MinIO через boto3
            s3_client.upload_fileobj(
                Fileobj=uploaded_file,
                Bucket=AWS_STORAGE_BUCKET_NAME,
                Key=file_name,
                ExtraArgs={"ContentType": uploaded_file.content_type},
            )

            # Генерируем ссылку на скачивание
            file_url = f"{s3_client.meta.endpoint_url}/{AWS_STORAGE_BUCKET_NAME}/{file_name}"
            return JsonResponse({"message": "Файл загружен в MinIO", "file_url": file_url})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Файл не был отправлен"}, status=400)
