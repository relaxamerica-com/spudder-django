from spudderaccounts.models import Invitation
from spudderdomain.controllers import CommunicationController
from spudderdomain.models import TeamAdministrator


class InvitationController(object):

    @classmethod
    def InviteNonUser(cls):
        pass

    @classmethod
    def InviteEntity(cls, invitee_entity_id, invitee_entity_type,
                     invitation_type, target_entity_id, target_entity_type):
        invitation, created = Invitation.objects.get_or_create(
            invitee_entity_id=invitee_entity_id,
            invitee_entity_type=invitee_entity_type,
            invitation_type=invitation_type,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            defaults={'status': Invitation.PENDING_STATUS})
        invitation.status = Invitation.PENDING_STATUS
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
