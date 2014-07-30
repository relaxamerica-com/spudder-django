from django.db import models
from django.contrib.auth.models import User
from djangotoolbox.fields import DictField

# Static variables for the 3 possible states
STATE_NEW = "new"
STATE_ACCEPTED = "accepted"
STATE_REJECTED = "rejected"

# Static variables for the 2 possible flag types
FLAG_INAPPROPRIATE = "inappropriate"
FLAG_INCORRECT = "incorrect"


class Flag(models.Model):
    """
    Contains everything about a flagged page, at the time of flagging.

    The custom_img and custom_text fields record the actually flagged
    content at the time of flagging. This is so that the admin can
    see what was flagged, even if there is a delay between the flag
    being created and the flag being reviewed by an admin.

    Although not (yet) checked, the model should contain flagger_user
    OR (flagger_name AND flagger_email) -- name and email can be
    stripped from the user object as needed, but this also provides
    a nice check to see whether the flag comes from a Spudder user
    or a guest.
    """
    url = models.CharField(max_length=200)
    owner = models.ForeignKey(User)
    state = models.CharField(max_length=8)  # rejected/accepted are 8 chars
    custom_text = DictField(null=True)
    custom_imgs = DictField(null=True)
    time = models.DateTimeField()
    flag_type = models.CharField(max_length=13)  # inappropriate is 13 chars
    comment = models.TextField(null=False)
    flagger_email = models.CharField(max_length=100, null=True)
    flagger_name = models.CharField(max_length=100, null=True)
    flagger_user = models.ForeignKey(User, null=True)

    def get_images_as_links(self):
        """
        Gets links for all images, corresponding to property name

        :return: a dict of <image property name>:<relative img url>
        """
        image_links = dict()
        for key in self.custom_imgs:
            url = '/file/serve/%s' % self.custom_imgs[key].id
            image_links[key] = url
        return image_links