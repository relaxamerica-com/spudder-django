from django.shortcuts import redirect
from spudderaccounts.utils import select_user_role_if_only_one_role_exists, select_all_user_roles, change_current_role
from spudderaccounts.wrappers import RoleBase
from spudderdomain.controllers import RoleController


class RolesMiddleware:
    def _add_current_role(self, request):
        current_role = None
        if request.user and request.user.is_authenticated():
            role_controller = RoleController(request.user)
            current_role = request.session.get('current_role', None)
            if not current_role:
                one_ane_only_role = select_user_role_if_only_one_role_exists(role_controller)
                if one_ane_only_role:
                    current_role = {
                        'entity_type': one_ane_only_role.entity_type,
                        'entity_id': one_ane_only_role.entity.id}
            if current_role:
                change_current_role(request, current_role['entity_type'], current_role['entity_id'])
                current_role = role_controller.role_by_entity_type_and_entity_id(
                    current_role['entity_type'],
                    current_role['entity_id'],
                    RoleBase.RoleWrapperByEntityType(current_role['entity_type']))
        request.current_role = current_role

    def _add_all_roles(self, request):
        all_roles = []
        if request.user and request.user.is_authenticated():
            role_controller = RoleController(request.user)
            all_roles = select_all_user_roles(role_controller)
        request.all_roles = all_roles

    def process_request(self, request):
        self._add_current_role(request)
        self._add_all_roles(request)
        if request.all_roles and len(request.all_roles) > 1:
            if not request.user.spudder_user.has_set_password:
                request.user.spudder_user.mark_as_password_required()


class AccountPasswordMiddleware:
    def process_request(self, request):
        path = '/users/account/create_password'
        if request.path != path and request.user and request.user.is_authenticated():
            spudder_user = request.user.spudder_user
            if spudder_user.needs_to_set_password and not spudder_user.has_set_password:
                return redirect("%s?next=%s" % (path, request.get_full_path()))