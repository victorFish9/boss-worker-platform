import asyncio
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .s3_client import MinIOClient



from rest_framework.permissions import IsAuthenticated

from .s3_client import MinIOClient




class UploadFileView(View):
    def get(self, request):
        file_path = request.GET.get("file_path")
        if not file_path:
            return JsonResponse({"error": "Укажите file_path"}, status=400)

        client = MinIOClient()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.upload_file(file_path))
        return JsonResponse({"message": result})


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
