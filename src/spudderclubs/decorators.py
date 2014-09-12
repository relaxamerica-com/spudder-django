from django.shortcuts import redirect
from spudderdomain.controllers import RoleController


def club_admin_required(function):
    def wrapper(request, *args, **kwargs):
        if request.current_role and request.current_role.entity_type == RoleController.ENTITY_CLUB_ADMIN:
            return function(request, *args, **kwargs)
        return redirect('/club/forbidden')
    return wrapper


def club_not_fully_activated(function):
    def wrapper(request, *args, **kwargs):
        if not request.current_role.entity.club.is_fully_activated():
            return function(request, *args, **kwargs)
        return redirect('/club/dashboard')
    return wrapper
