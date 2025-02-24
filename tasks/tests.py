from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

class MinIOFileDownloadTest(TestCase):
    @patch("tasks.storage.s3_client.generate_presigned_url")
    def test_download_link_generation(self, mock_generate_presigned_url):
        mock_generate_presigned_url.return_value = "http://localhost:9000/bossworker/test.txt?mocked-url"
        response = self.client.get(reverse("get_file_link", args=["test.txt"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["download_url"], "http://localhost:9000/bossworker/test.txt?mocked-url")