from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import os
import json

SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = "11T7jAQ_Hup5lG9oxvcWydXo3GMJpVqqR"


import os
import json

def authenticate():
    service_json_str = os.getenv("SERVICE_JSON")
    if not service_json_str:
        raise FileNotFoundError("SERVICE_JSON not found in environment variables")


    service_json_str = service_json_str.replace("\\n", "\n")
    service_json = json.loads(service_json_str)

    creds = service_account.Credentials.from_service_account_info(service_json, scopes=SCOPES)
    return creds



def upload_large_file_to_drive(file_path, file_name):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [PARENT_FOLDER_ID]
    }

    media = MediaFileUpload(file_path, chunksize=50 * 1024 * 1024, resumable=True)  # Разбиваем на 50MB

    request = service.files().create(body=file_metadata, media_body=media, fields="id")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Загрузка: {int(status.progress() * 100)}%")  # Показываем прогресс

    os.remove(file_path)  # Удаляем файл после загрузки

    return response.get("id")


@csrf_exempt
def upload_to_google_drive(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_path = os.path.join("/tmp", uploaded_file.name)

        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
            file_id = upload_large_file_to_drive(file_path, uploaded_file.name)
            return JsonResponse({"message": "Файл загружен в Google Drive", "file_id": file_id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Файл не был отправлен"}, status=400)
