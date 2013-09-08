from django import template
register = template.Library()

@register.inclusion_tag('commons/display_items.html')
def display_items(div_id, title):
    return { 'id' : div_id, 'title' : title }

@register.inclusion_tag('commons/display_users.html')
def display_users(users, orientation, max_users):
    return { 'users' : users[:max_users], 'orientation' : orientation, 'max_users' : max_users }