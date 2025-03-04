import asyncio
import io
import uuid
import zipfile
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

from .s3_client import MinIOClient

from .models import FileDownload, UploadedFile




class UploadFilesAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if "files" not in request.FILES:
            return Response({"error": "Файлы не найдены"}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist("files")  # Получаем список файлов
        zip_buffer = io.BytesIO()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        zip_filename = f"uploaded_{timestamp}_{unique_id}.zip"

        # Создаём ZIP-архив
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                zip_file.writestr(file.name, file.read())

        zip_buffer.seek(0)

        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.upload_file(zip_filename, zip_buffer.read()))

        if "Ошибка" in result:
            return Response({"error": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Получаем URL для скачивания
        download_url = loop.run_until_complete(client.get_presigned_url(zip_filename))

        description = request.data.get("description", f"ZIP-архив из {len(files)} файлов")

        # Сохраняем в БД
        uploaded_file = UploadedFile.objects.create(
            filename=zip_filename,
            download_url=download_url,
            user=request.user,
            description=description
        )

        return Response({
            "message": "Архив успешно загружен",
            "filename": uploaded_file.filename,
            "download_url": uploaded_file.download_url,
            "uploaded_at": uploaded_file.uploaded_at,
            "description": uploaded_file.description
        }, status=status.HTTP_201_CREATED)

class ListFilesView(View):
    def get(self, request):
        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        files = loop.run_until_complete(client.list_bucket_objects())
        return JsonResponse({"files": files})

class ListFilesAPIView(APIView):
    def get(self, request):
        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        files = loop.run_until_complete(client.list_bucket_objects())
        return Response({"files": files}, status=status.HTTP_200_OK)

class FileDownloadAPIView(APIView):
    def get(self, request, filename):
        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        download_url = loop.run_until_complete(client.get_presigned_url(filename))

        if download_url:
            FileDownload.objects.create(
                user=request.user,
                file_name=filename,
                download_url=download_url,
                description=f"File {filename} was created"
            )
            return Response({"download_url": download_url}, status=status.HTTP_200_OK)
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

class GetFileLinkView(View):
    def get(self, request):
        file_name = request.GET.get("file_name")
        if not file_name:
            return JsonResponse({"error": "Укажите file_name"}, status=400)

        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        url = loop.run_until_complete(client.get_presigned_url(file_name))
        return JsonResponse({"url": url})

class StorageAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        files = loop.run_until_complete(client.list_bucket_objects())

        file_data = []
        for file in files:
            download_url = loop.run_until_complete(client.get_presigned_url(file))
            file_data.append({"filename": file, "download_url": download_url})



        return Response({"files": file_data}, status=status.HTTP_200_OK)
