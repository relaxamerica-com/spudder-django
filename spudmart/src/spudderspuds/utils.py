from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleBase
from spudderdomain.controllers import RoleController
from spudderdomain.models import FanPage


def create_and_activate_fan_role(request, user):
    fan, _ = FanPage.objects.get_or_create(fan=user)
    fan.save()
    role_controller = RoleController(user)
    role_controller.role_by_entity_type_and_entity_id(
        RoleController.ENTITY_FAN,
        fan.id,
        RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_FAN))
    change_current_role(request, RoleController.ENTITY_FAN, fan.id)