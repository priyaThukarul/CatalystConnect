from django.db import models
from chunked_upload.models import ChunkedUpload

class MyChunkedUpload(ChunkedUpload):
    # Add fields as needed to store metadata about the uploaded file
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Company_data(models.Model):
    name = models.CharField(max_length=1024)
    domain = models.CharField(max_length=1024)
    year_founded = models.IntegerField()
    industry = models.CharField(max_length=1024)
    size_range = models.CharField(max_length=1024)
    locality = models.CharField(max_length=1024)
    city = models.CharField(max_length=1024, null=True, blank=True)
    state = models.CharField(max_length=1024, null=True, blank=True)
    country = models.CharField(max_length=1024)
    linkedin_url = models.CharField(max_length=1024, null=True, blank=True)
    current_employee_estimate = models.IntegerField()
    total_employee_estimate = models.IntegerField()

class UploadSession(models.Model):
    upload_id = models.CharField(max_length=100, unique=True)
    file_name = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=10)
    total_chunks = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class FileChunk(models.Model):
    session = models.ForeignKey(UploadSession, on_delete=models.CASCADE)
    chunk_number = models.IntegerField()
    chunk_data = models.BinaryField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
