from django.contrib.auth.models import User
from django.db import models
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField

class Venue(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length = 200, default="This could be Your company")
    aka_name = models.CharField(max_length = 200, default="Common Venue Name")
    sport = models.CharField(max_length = 100)
    logo = models.ForeignKey(UploadedFile, null = True)
    speciality = models.CharField(max_length = 200)
    location = models.CharField(max_length = 200)
    coordinates = models.CharField(max_length = 100)
    latitude = models.DecimalField(null = True, decimal_places = 6, max_digits = 10)
    longitude = models.DecimalField(null = True, decimal_places = 6, max_digits = 10)
    parking_details = models.CharField(max_length = 200)
    parking_tips = models.CharField(max_length = 200)
    video = models.CharField(max_length = 300)
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

    # Just to stay consistent with fcns created in campusrep.rep
    rep = models.IntegerField()
    level = models.IntegerField()
    
    def __eq__(self, other):
        return self.pk == other.pk
    
