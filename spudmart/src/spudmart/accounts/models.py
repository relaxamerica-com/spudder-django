from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    amazon_id = models.CharField(null=True, blank=True)
    amazon_access_token = models.CharField(null=True, blank=True)
    spudder_id = models.CharField()