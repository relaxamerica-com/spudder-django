from django.conf import settings


def current_role_context(request):
    """
    Exposes the current role to the template context
    :param request: the Django request object
    :return: dict with the current_role set to the appropriate subclass of spudderaccounts.wrappers.RoleBase
    """
    if request.current_role:
        return {'current_role': request.current_role}
    return {}


def other_roles_context(request):
    """
    Exposes all user roles to the template context

    :param request: the Django request object
    :return: dict with the all_roles set to a list of all user roles as subclass of spudderaccounts.wrappers.RoleBase
    """
    if request.all_roles and request.current_role:
        other_roles = [r for r in request.all_roles if r.entity.id != request.current_role.entity.id]
        return {'other_roles': other_roles}
    return {}


def amazon_client_id(_):
    return {'AMAZON_CLIENT_ID': settings.AMAZON_LOGIN_CLIENT_ID}