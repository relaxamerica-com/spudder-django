from django import template

register = template.Library()

@register.filter
def get_venue_tags(text):
    tags = text.split(' ')
    tags.pop(-1) # remove the last tag, beacuse it's the Venue itself
    return tags