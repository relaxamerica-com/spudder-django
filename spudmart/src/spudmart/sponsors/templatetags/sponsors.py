from django import template

register = template.Library()

@register.filter(name='location_external_link')
def location_external_link(map_info):
    start_index = map_info.index('href="') + 6
    end_index = map_info.index(' target') - 1

    return map_info[start_index:end_index]