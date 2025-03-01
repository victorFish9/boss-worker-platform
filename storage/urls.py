from django.urls import path
from .views import UploadFileView, ListFilesView, GetFileLinkView, ListFilesAPIView, FileDownloadAPIView, StorageAPIView

urlpatterns = [
    path("upload/", UploadFileView.as_view(), name="upload-file"),
    path("list/", ListFilesAPIView.as_view(), name="list-files"),
    path("download/<str:filename>/", FileDownloadAPIView.as_view(), name="download-file"),
    path("file-link/", GetFileLinkView.as_view(), name="get-file-link"),
    path("storage/", StorageAPIView.as_view(), name="storage"),
]
