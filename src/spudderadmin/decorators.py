from functools import wraps
from django.shortcuts import redirect
from spudderadmin.utils import encoded_admin_session_variable_name


# def admin_login_required():
#     def decorator(func):
#         def inner_decorator(request, *args, **kwargs):
#             if not request.session.get(encoded_admin_session_variable_name(), False):
#                 return redirect('admin_login')
#             return func(request, *args, **kwargs)
#         return wraps(func)(inner_decorator)
#     return decorator
#

def admin_login_required(function):
    def wrap(request, *args, **kwargs):

        if not request.session.get(encoded_admin_session_variable_name(), False):
            return redirect('/spudderadmin')
        return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
    return wrap