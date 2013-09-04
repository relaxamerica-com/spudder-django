from django.db import models
from django.contrib.auth.models import User

class ProfileType():
    FAN = 1

class Profile(models.Model):
    type = models.IntegerField(default = ProfileType.FAN)
    user = models.ForeignKey(User)