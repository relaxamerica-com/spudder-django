from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from spudderaccounts.models import Invitation, Notification
from spudderaccounts.wrappers import RoleBase
from spudderdomain.controllers import CommunicationController, RoleController, EntityController
from spudderdomain.models import TeamAdministrator, FanPage


class InvitationController(object):

    @classmethod
    def InviteNonUser(cls, invitee_email, invitation_type, target_entity_id,
                      target_entity_type, extras={}):
        invitation, created = Invitation.objects.get_or_create(
            invitee_entity_id=invitee_email,
            invitation_type=invitation_type,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            defaults={'status': Invitation.PENDING_STATUS})
        invitation.status = Invitation.PENDING_STATUS
        if created and extras:
            invitation.extras = extras
        invitation.save()
        CommunicationController.CommunicateWithNonUserByEmail(
            invitee_email,
            invitation=invitation,
            communication_type=CommunicationController.TYPE_EMAIL)

    @classmethod
    def InviteEntity(cls, invitee_entity_id, invitee_entity_type,
                     invitation_type, target_entity_id, target_entity_type,
                     extras={}):
        invitation, created = Invitation.objects.get_or_create(
            invitee_entity_id=invitee_entity_id,
            invitee_entity_type=invitee_entity_type,
            invitation_type=invitation_type,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            defaults={'status': Invitation.PENDING_STATUS})
        invitation.status = Invitation.PENDING_STATUS
        if created and extras:
            invitation.extras = extras
        invitation.save()
        CommunicationController.CommunicateWithEntity(
            invitee_entity_id, invitee_entity_type,
            invitation=invitation,
            communication_type=CommunicationController.TYPE_EMAIL)

    @classmethod
    def CancelEntityInvitation(cls, invitee_entity_id, invitee_entity_type,
                     invitation_type, target_entity_id, target_entity_type):
        invitation = Invitation.objects.get(
            invitee_entity_id=invitee_entity_id,
            invitee_entity_type=invitee_entity_type,
            status=Invitation.PENDING_STATUS,
            invitation_type=invitation_type,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type
        )
        invitation.status = Invitation.CANCELED_STATUS
        invitation.save()
        CommunicationController.CommunicateWithEntity(
            invitee_entity_id, invitee_entity_type,
            invitation=invitation,
            communication_type=CommunicationController.TYPE_EMAIL)

    @classmethod
    def RevokeEntityInvitation(cls, invitee_entity_id, invitee_entity_type,
                     invitation_type, target_entity_id, target_entity_type):

        if invitation_type in Invitation.INVITATION_TYPES:
            if invitation_type == Invitation.ADMINISTRATE_TEAM_INVITATION:
                TeamAdministrator.objects.filter(
                    entity_type=invitee_entity_type,
                    entity_id=invitee_entity_id,
                    team_page__id=target_entity_id).delete()
            else:
                raise NotImplementedError('Invitation type %s not implemented')
        else:
            raise NotImplementedError('Invitation type %s not supported')

        invitation, created = Invitation.objects.get_or_create(
            invitee_entity_id=invitee_entity_id,
            invitee_entity_type=invitee_entity_type,
            invitation_type=invitation_type,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            defaults={'status': Invitation.ACCEPTED_STATUS})
        invitation.status = Invitation.REVOKED_STATUS
        invitation.save()
        CommunicationController.CommunicateWithEntity(
            invitee_entity_id, invitee_entity_type,
            invitation=invitation,
            communication_type=CommunicationController.TYPE_EMAIL)

    @classmethod
    def CheckFanWithEmailExists(cls, email):
        try:
            u = User.objects.get(email=email)
        except ObjectDoesNotExist:
            try:
                return FanPage.objects.get(email=email)
            except ObjectDoesNotExist:
                pass
        else:
            try:
                return FanPage.objects.get(user=u)
            except ObjectDoesNotExist:
                pass
        return None

    @classmethod
    def GetAllAdminsAndInvitesForTeam(cls, team_page):
        team_admins_ids = TeamAdministrator.objects \
            .filter(team_page=team_page, entity_type=RoleController.ENTITY_FAN).values_list('entity_id', flat=True)
        team_admins_ids = [int(fan_id) for fan_id in team_admins_ids]
        admins = FanPage.objects.filter(id__in=team_admins_ids)
        # get invited fans
        invited_fans_ids = Invitation.objects.filter(
            invitee_entity_type=RoleController.ENTITY_FAN,
            invitation_type=Invitation.ADMINISTRATE_TEAM_INVITATION,
            status=Invitation.PENDING_STATUS,
            target_entity_id=team_page.id,
            target_entity_type=EntityController.ENTITY_TEAM
        ).values_list('invitee_entity_id', flat=True)
        invited_fans_ids = [int(fan_id) for fan_id in invited_fans_ids]
        invited_fans = FanPage.objects.filter(id__in=invited_fans_ids)
        # get not invited fans
        invited_or_admin_ids = list(team_admins_ids) + list(invited_fans_ids)
        not_invited_fans = FanPage.objects.exclude(id__in=invited_or_admin_ids)
        # get invited non-users
        invited_non_users = Invitation.objects.filter(
            invitation_type=Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION,
            status=Invitation.PENDING_STATUS,
            target_entity_id=team_page.id,
            target_entity_type=EntityController.ENTITY_TEAM
        ).order_by('-modified')

        return admins, invited_fans, invited_non_users, not_invited_fans


class NotificationController(object):
    NOTIFY_BY_EMAIL = 'notify_by_email'
    NOTIFICATION_CHANNELS = (NOTIFY_BY_EMAIL, )

    @classmethod
    def NotifyEntity(cls, target_entity_id, target_entity_type, notification_type,
                     extras={}, notification_channels=[NOTIFY_BY_EMAIL]):

        notifications = Notification.objects.filter(target_entity_id=target_entity_id,
                                                    target_entity_type=target_entity_type,
                                                    notification_type=notification_type)
        created = False
        notify_after = extras.get('notify_after')
        for notification in notifications:
            if notification.extras.get('notify_after') == notify_after:
                created = True
                break

        if not created:
            notification = Notification(
                target_entity_id=target_entity_id,
                target_entity_type=target_entity_type,
                notification_type=notification_type,
                extras=extras)
            notification.save()

        for notification_channel in notification_channels:
            if notification_channel in cls.NOTIFICATION_CHANNELS:
                if notification_channel == cls.NOTIFY_BY_EMAIL:
                    if notification_type == Notification.COMPLETE_CHALLENGE_NOTIFICATION and not created:
                        entity = RoleController.GetRoleForEntityTypeAndID(
                            target_entity_type, target_entity_id, RoleBase.RoleWrapperByEntityType(target_entity_type))
                        kwargs = {'notification': notification}
                        CommunicationController.CommunicateWithEmail(emails=entity.contact_emails, **kwargs)
                else:
                    raise NotImplementedError('Notification channel %s not implemented' % notification_channel)
            else:
                raise NotImplementedError('Notification channel %s not supported' % notification_channel)
