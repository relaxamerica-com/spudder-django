from spudderaccounts.wrappers import RoleBase


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
    if len(roles) == 1:
        return roles[0]
    return None
