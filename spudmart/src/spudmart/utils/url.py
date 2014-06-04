def get_return_url(request, default='/'):
    return request.GET.get("next", default)

def get_request_param(request, param, default=''):
    return request.GET.get(param, default)