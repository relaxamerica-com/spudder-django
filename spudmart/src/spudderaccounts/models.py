from django.contrib.auth.models import User
from django.db import models


class SpudderUser(models.Model):
    user = models.ForeignKey(User)
    needs_to_set_password = models.BooleanField(default=False)
    has_set_password = models.BooleanField(default=False)

    def mark_as_password_required(self):
        self.needs_to_set_password = True
        self.save()
        return self

    def mark_password_as_done(self):
        self.needs_to_set_password = False
        self.has_set_password = True
        self.save()
        return self

User.spudder_user = property(lambda u: SpudderUser.objects.get_or_create(user=u)[0])