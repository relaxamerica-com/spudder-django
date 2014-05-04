from django.db import models


class UploadedFile(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/')
    content_type = models.CharField(max_length=200, null=True)
    filename = models.CharField(max_length=200, null=True)