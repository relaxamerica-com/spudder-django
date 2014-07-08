from django.db import models
from djangotoolbox.fields import ListField
from django.contrib.auth.models import User
from spudmart.upload.models import UploadedFile

class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)  # what user should be used here?
    text = models.TextField()


class SpudType():
    TEXT = 1
    VIDEO = 2
    IMAGE = 3


class Spud(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    tags = ListField()
    type = models.IntegerField(choices = ((SpudType.TEXT, 'Text'), 
                                          (SpudType.VIDEO, 'Video'), 
                                          (SpudType.IMAGE, 'Image')), default = SpudType.TEXT)
    comments = ListField(Comment)
    content = models.TextField()
    image = models.ForeignKey(UploadedFile, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    author = models.ForeignKey(User)  # what user should be used here?
    
    def tags_to_string(self):
        return ' '.join(self.tags)
    
    