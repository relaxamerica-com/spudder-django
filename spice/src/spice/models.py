from django.db import models

class APIKeys(models.Model):
    api_key = models.CharField(max_length=20)
    is_active = models.BooleanField()
