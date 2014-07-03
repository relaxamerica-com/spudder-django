from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def change_role_and_return_url(context, role):
    return '/users/roles/activate/%s/%s?next=%s' % (
        role.entity_type, role.entity.id, context['request'].path)