from django.db import models


class Affiliate(models.Model):
    """
    A simple model to hold everything about an affiliate.
    """
    name = models.CharField(max_length=256)
    url_name = models.CharField(max_length=256)
    description = models.TextField()
    path_to_icon = models.CharField(max_length=256)
    path_to_cover_image = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
