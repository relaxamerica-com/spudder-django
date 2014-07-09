from django.contrib.auth import authenticate
from spudderaccounts.wrappers import RoleBase, AuthenticationServiceBase
from spudderdomain.controllers import LinkedServiceController, RoleController


def change_role_url(role):
    return '/users/roles/activate/%s/%s' % (role.entity_type, role.entity.id)


def select_all_user_roles(role_controller):
    """
    Returns a list of all user roles in the right wrapper
    :param role_controller: spudderdomain.controllers.RoleController instance
    :return: list of wrappers subclassed from apudderaccounts.wrappers.RoleBase
    """
    roles = []
    for entity_type in role_controller.ENTITY_TYPES:
        roles += role_controller.roles_by_entity(entity_type, RoleBase.RoleWrapperByEntityType(entity_type))
    roles.sort(key=lambda r: r.meta_data.get('last_accessed', 0), reverse=True)
    return roles


def select_user_role_if_only_one_role_exists(role_controller):
    """
    Check if the user has only one role, if it does then return it, if not then return None

    :param role_controller: spudderdomain.controllers.RoleController instance
    :return: Either the one and only role the user has or None
    """
    roles = select_all_user_roles(role_controller)
    if len(roles):  # == 1: TODO: This needs to be implemented alongside a highlevel role chooing page
        return roles[0]
    return None


def select_authentication_services_for_role(role):
    """
    Selects all the linked authentication services for a given role

    :param role: An instance of RoleBase of one of its subclasses
    :return: Collection of subclasses of LinkedServiceBase
    """
    linked_service_controller = LinkedServiceController(role)
    return [
        AuthenticationServiceBase.RoleWrapperByEntityType(linked_service.service_type)(linked_service)
        for linked_service in linked_service_controller.linked_services(
            type_filtes=AuthenticationServiceBase.AUTHENTICATION_SERVICE_TYPES)]


def select_role_by_authentication_service(service_type, unique_service_id):
    service_wrapper = LinkedServiceController.LinkedServiceByTypeAndID(
        service_type,
        unique_service_id,
        AuthenticationServiceBase.RoleWrapperByEntityType(service_type))
    if not service_wrapper:
        return None
    return RoleController.GetRoleForEntityTypeAndID(
        service_wrapper.linked_service.role_type,
        service_wrapper.linked_service.role_id,
        RoleBase.RoleWrapperByEntityType(service_wrapper.linked_service.role_type))


def get_authentication_wrapper(role, service_type, unique_service_id):
    if service_type != LinkedServiceController.SERVICE_AMAZON:
        raise NotImplementedError("the service type %s is not yet supported by this method" % service_type)
    return LinkedServiceController.LinkedServiceByTypeAndID(
        service_type,
        unique_service_id,
        AuthenticationServiceBase.RoleWrapperByEntityType(service_type))


def create_linked_authentication_service(role, service_type, unique_service_id, configuration):
    linked_service_controller = LinkedServiceController(role)
    linked_service_wrapper = linked_service_controller.create_linked_service(
        service_type,
        unique_service_id,
        configuration,
        AuthenticationServiceBase.RoleWrapperByEntityType(service_type))
    return linked_service_wrapper