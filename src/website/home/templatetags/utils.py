from django import template
register = template.Library()

@register.inclusion_tag('commons/display_items.html')
def display_items(div_id, title):
    return { 'id' : div_id, 'title' : title }