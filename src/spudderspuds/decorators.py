from functools import wraps
from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden


def can_edit(function):
    def wrap(request, *args, **kwargs):
        if not hasattr(request, 'can_edit') or not request.can_edit:
            return HttpResponseForbidden()
        return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
    return wrap



    #
    # (func):
    # """
    # Decorator to make a view only accept if request.can_edit is True.  Usage::
    #
    #     @can_edit(["GET", "POST"])
    #     def my_view(request):
    #         # ...
    #
    # """
    # def decorator(func):
    #     @wraps(func, assigned=available_attrs(func))
    #     def inner(request, *args, **kwargs):
    #         raise Exception
    #         if hasattr(request, 'can_edit') and not request.can_edit:
    #             return HttpResponseForbidden()
    #         return func(request, *args, **kwargs)
    #     return inner
    # return decorator
