from django.shortcuts import redirect
from spudderdomain.controllers import RoleController


def current_role_is_sponsor(function):
    def wrap(request, *args, **kwargs):

        if request.current_role and request.current_role.entity_type == RoleController.ENTITY_SPONSOR:
            return function(request, *args, **kwargs)
        return redirect('/sponsor/non_sponsor')

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
    return wrap
