from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/')
    content_type = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
