from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def link_to_change_role_and_return(context, role):
    return '/users/roles/activate/%s/%s?next=%s' % (
        role.entity_type, role.entity.id, context['request'].path)


@register.simple_tag
def link_to_role_management_page(role):
    return '/users/roles/manage/%s/%s' % (role.entity_type, role.entity.id)


@register.simple_tag(takes_context=True)
def link_to_delete_role_and_return(context, role):
    return '/users/roles/delete/%s/%s?next=%s' % (
        role.entity_type, role.entity.id, context['request'].path)