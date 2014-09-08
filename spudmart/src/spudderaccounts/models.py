from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


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


class Invitation(models.Model):

    ADMINISTRATE_TEAM_INVITATION = 'administrate_team'

    INVITATION_TYPES = (ADMINISTRATE_TEAM_INVITATION, )

    INVITATION_CHOICES = (
        (ADMINISTRATE_TEAM_INVITATION, 'Administrate team'),
    )

    PENDING_STATUS = 'pending'
    CANCELED_STATUS = 'canceled'
    REVOKED_STATUS = 'revoked'
    REJECTED_STATUS = 'rejected'
    ACCEPTED_STATUS = 'accepted'

    STATUS_CHOICES = (
        (PENDING_STATUS, 'Pending'),
        (CANCELED_STATUS, 'Canceled'),
        (REVOKED_STATUS, 'Revoked'),
        (REJECTED_STATUS, 'Rejected'),
        (ACCEPTED_STATUS, 'Accepted'),
    )

    invitee_entity_id = models.CharField(max_length=255)
    invitee_entity_type = models.CharField(max_length=255)
    invitation_type = models.CharField(max_length=255, choices=INVITATION_CHOICES)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    target_entity_id = models.CharField(max_length=255)
    target_entity_type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def link(self):
        if self.invitation_type == self.ADMINISTRATE_TEAM_INVITATION:
            return "%s/team/%s/accept_fan_invitation/%s" % (settings.SPUDMART_BASE_URL, self.target_entity_id, self.id)
