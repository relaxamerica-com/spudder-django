from django import template
from spudderaccounts.utils import change_role_url
from spudderdomain.controllers import RoleController

register = template.Library()


@register.simple_tag
def link_to_change_role_and_return(role, next_url=None):
    if not next_url:
        next_url = role.home_page_path

    return '%s?next=%s' % (change_role_url(role), next_url)


@register.simple_tag
def link_to_role_management_page(role):
    return '/users/roles/manage/%s/%s' % (role.entity_type, role.entity.id)


@register.simple_tag(takes_context=True)
def link_to_delete_role_and_return(context, role):
    return '/users/roles/delete/%s/%s?next=%s' % (
        role.entity_type, role.entity.id, context['request'].path)


@register.filter
def is_cern_student(role):
    return role.entity_type == RoleController.ENTITY_STUDENT


@register.filter
def is_sponsor(role):
    return role.entity_type == RoleController.ENTITY_SPONSOR


@register.filter
def is_fan(role):
    return role and role.entity_type == RoleController.ENTITY_FAN


@register.filter
def is_club_admin(role):
    return role and role.entity_type == RoleController.ENTITY_CLUB_ADMIN


@register.filter
def user_has_fan_role(request):
    for role in request.all_roles:
        if is_fan(role):
            return True
    return False


@register.filter
def user_has_club_admin_role(request):
    for role in request.all_roles:
        if is_club_admin(role):
            return True
    return False


@register.simple_tag
def link_to_change_role_to_club_admin(request):
    for role in request.all_roles:
        if is_club_admin(role):
            return '%s?next=%s' % (change_role_url(role), role.home_page_path)

    return ''