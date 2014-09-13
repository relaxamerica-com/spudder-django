import os


def get_return_url(request, default='/'):
    return request.GET.get("next", default)


def get_request_param(request, param, default=''):
    return request.GET.get(param, default)


def determine_ssl():
    return not os.environ['SERVER_SOFTWARE'].startswith('Development')