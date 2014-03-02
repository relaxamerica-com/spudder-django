from django import template

register = template.Library()

@register.inclusion_tag('home/displays/sports.html')
def display_sports(id):
    return { 'id': id }