from django.template.defaulttags import register


@register.filter()
def progress_bar_value(la_import):
    # return round(la_import.progress * 100,  2)
    return "{0:.2f}".format(round(la_import.progress * 100,2))
