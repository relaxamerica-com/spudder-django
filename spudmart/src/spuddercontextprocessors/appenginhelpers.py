import os


def context_running_locally(request):
    """
    Allows template to use the running_locally boolean variable to see if the application is running locally or
    on appengine

    To use this context variable, this file must be included in the TEMPLATE_CONTEXT_PROCESSORS tuple in the
    settings.py file

    :param request: The current request
    :return: dict, additions to the template context
    """
    return {
        'running_locally': bool(os.environ['SERVER_SOFTWARE'].startswith('Development'))
    }