from django.urls import path
from .views import upload_to_minio

urlpatterns = [
    #path("download/<str:file_name>/", get_file_link, name="get_file_link"),
    path("upload/", upload_to_minio, name="upload_to_minio"),
]