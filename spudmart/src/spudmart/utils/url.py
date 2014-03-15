def get_return_url(request, default='/'):
    return request.GET.get("next", default)
