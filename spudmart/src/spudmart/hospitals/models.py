from django.contrib.auth.models import User
from django.db import models
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField

class Hospital(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length = 100)
    address1 = models.CharField(max_length = 100)
    address2 = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    state = models.CharField(max_length = 100)
    zip = models.CharField(max_length = 10)
    county_name = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 100)
    latitude = models.DecimalField(null = True, decimal_places = 6, max_digits = 9)
    longitude = models.DecimalField(null = True, decimal_places = 6, max_digits = 9)
    
    def __eq__(self, other):
        return self.pk == other.pk
    
