from django.contrib.auth.models import User
from django.db import models
from spudmart.upload.models import UploadedFile

class Venue(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length = 200)
    aka_name = models.CharField(max_length = 200)
    logo = models.ForeignKey(UploadedFile)
    speciality = models.CharField(max_length = 200)
    location = models.CharField(max_length = 200)
    phone = models.CharField(max_length = 200)
    email = models.CharField(max_length = 200)
    website = models.CharField(max_length = 200)
    fax = models.CharField(max_length = 200)
