from django.urls import path
from .views import upload_to_google_drive

urlpatterns = [
    #path("download/<str:file_name>/", get_file_link, name="get_file_link"),
    path("upload/", upload_to_google_drive, name="upload_to_drive"),
]