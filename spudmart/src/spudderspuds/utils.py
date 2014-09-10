from django.contrib import messages
from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleBase, RoleFan
from spudderdomain.controllers import RoleController, SpudsController
from spudderdomain.models import FanPage
from spuddersocialengine.models import SpudFromSocialMedia
from functools import wraps
from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden


def create_and_activate_fan_role(request, user):
    fan, _ = FanPage.objects.get_or_create(fan=user)
    fan.save()
    role_controller = RoleController(user)
    role_controller.role_by_entity_type_and_entity_id(
        RoleController.ENTITY_FAN,
        fan.id,
        RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_FAN))
    change_current_role(request, RoleController.ENTITY_FAN, fan.id)
    return RoleFan(fan)


def is_signin_claiming_spud(request, fan, twitter, spud_id):
    if twitter:
        fan.twitter = twitter
        fan.save()
        if spud_id:
            controller = SpudsController(RoleFan(fan))
            spud = SpudFromSocialMedia.objects.get(id=spud_id)
            controller.add_spud_from_fan(spud)
            messages.success(
                request,
                "You twitter name to <b>%s</b> and you claimed your SPUD!" % twitter)


def set_social_media(entity, form):
    for attr in form.get_social_media():
        entity.__setattr__(attr, form.cleaned_data.get(attr, ''))


def can_edit():
    """
    Decorator to make a view only accept if request.can_edit is True.  Usage::

        @can_edit(["GET", "POST"])
        def my_view(request):
            # ...

    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if not request.can_edit:
                return HttpResponseForbidden()
            return func(request, *args, **kwargs)
        return inner
    return decorator
