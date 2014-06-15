from django.contrib.auth.models import User
from django.db import models


class SystemMessage(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, null=True)
    body = models.TextField(default='')
    delivered = models.BooleanField(default=False)