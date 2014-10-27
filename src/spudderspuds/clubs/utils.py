from spudderdomain.controllers import EntityController
from spudderdomain.wrappers import EntityBase


def get_club_and_club_entity(request):
    club = request.current_role.entity.club
    club_entity = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_CLUB,
        club.id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_CLUB))
    return club, club_entity