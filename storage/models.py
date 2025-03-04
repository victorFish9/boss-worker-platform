from django.db import models
from django.contrib.auth.models import User

class FileDownload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    download_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file_name}"


class StoredFile(models.Model):
    filename = models.CharField(max_length=255)  # Название файла
    download_url = models.URLField()  # URL для скачивания
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пользователь, запрашивающий ссылку
    retrieved_at = models.DateTimeField(auto_now_add=True)  # Время запроса

    def __str__(self):
        return f"{self.filename} - {self.user.username}"


class UploadedFile(models.Model):
    filename = models.CharField(max_length=255)  # Название файла
    download_url = models.URLField()  # URL для скачивания
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Кто загрузил файл
    description = models.TextField(blank=True, null=True)  # Описание файла
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Дата загрузки

    def __str__(self):
        return f"{self.filename} - {self.user.username}"

