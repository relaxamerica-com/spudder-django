from django.contrib.auth.models import User
from django.db import models
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField

class Venue(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length = 200, default="This could be Your company")
    aka_name = models.CharField(max_length = 200, default="AKA - Common Venue Name")
    logo = models.ForeignKey(UploadedFile, null=True)
    speciality = models.CharField(max_length = 200)
    location = models.CharField(max_length = 200)
    coordinates = models.CharField(max_length = 100)
    parking_details = models.CharField(max_length = 200)
    parking_tips = models.CharField(max_length = 200)
    video = models.CharField(max_length = 100)
    venue_pics = ListField()
    playing_surface_pics = ListField()
    playing_surface_details = models.CharField(max_length = 200)
    restroom_details = models.CharField(max_length = 200)
    concession_details = models.CharField(max_length = 200)
    admission_details = models.CharField(max_length = 200)
    shelter_details = models.CharField(max_length = 200)
    medical_details = models.CharField(max_length = 200)
    medical_address = models.CharField(max_length = 200)
    handicap_details = models.CharField(max_length = 200)
    phone = models.CharField(max_length = 200)
    email = models.CharField(max_length = 200)
    website = models.CharField(max_length = 200)
    price = models.IntegerField(default = 0)
    fax = models.CharField(max_length = 200)
    
