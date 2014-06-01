from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    amazon_id = models.CharField(null=True, blank=True, max_length=255)
    amazon_access_token = models.CharField(null=True, blank=True, max_length=255)
    spudder_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)