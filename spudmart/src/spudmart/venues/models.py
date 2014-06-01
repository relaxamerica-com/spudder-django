from django.contrib.auth.models import User
from django.db import models
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField
from spudmart.CERN.models import get_max_triangle_num_less_than, VENUE_REP_LEVEL_MODIFIER


class Venue(models.Model):
    user = models.ForeignKey(User, related_name="owner_user")
    renter = models.ForeignKey(User, null= True, related_name="renter_user")
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
    price = models.DecimalField(default = 0.0, decimal_places = 2, max_digits = 10)
    fax = models.CharField(max_length = 200)

    # Just to stay consistent with fcns created in campusrep.rep
    rep = models.IntegerField(default=0)
    
    def level(self):
        return get_max_triangle_num_less_than(self.rep / VENUE_REP_LEVEL_MODIFIER)
    
    def __eq__(self, other):
        return self.pk == other.pk