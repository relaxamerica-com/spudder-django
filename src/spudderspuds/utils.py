import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from spudderaccounts.models import Invitation
from spudderaccounts.templatetags.spudderaccountstags import is_fan, user_has_fan_role
from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleBase, RoleFan
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderdomain.controllers import RoleController, SpudsController
from spudderdomain.models import FanPage
from spudderkrowdio.utils import start_following
from spuddersocialengine.models import SpudFromSocialMedia


def create_and_activate_fan_role(request, user):
    # get or create fan role
    fan, created = FanPage.objects.get_or_create(fan=user)
    fan.save()

    # set new users to follow dennis@spudder.com fan
    if feature_is_enabled('all_fans_auto_follow_main_spudder_fan') and created:
        main_account = User.objects.get(email=settings.MAIN_SPUDDER_FAN_ACCOUNT_EMAIL)
        main_fan = FanPage.objects.get(fan=main_account)
        current_entity = RoleController.GetRoleForEntityTypeAndID(
            RoleController.ENTITY_FAN,
            fan.id,
            RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_FAN))
        start_following(current_entity, RoleController.ENTITY_FAN, main_fan.id)

    # activate role
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


def should_current_role_be_here(request):
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_FAN:
        return False, redirect('/spuds')
    if request.current_role and not is_fan(request.current_role) and not user_has_fan_role(request):
        if request.GET.get('twitter', None) and request.GET.get('spud_id', None):
            return False, redirect(
                '/spuds/register_add_fan_role?twitter=%s&spud_id=%s' %
                (request.GET['twitter'], request.GET['spud_id']))
        else:
            return False, redirect('/spuds/register_add_fan_role')
    return True, None


def extract_invitation_from_request(request):
    invitation_id = request.session.get('invitation_id')
    invitation = None
    if invitation_id:
        try:
            invitation = Invitation.objects.get(id=invitation_id, status=Invitation.PENDING_STATUS)
        except Invitation.DoesNotExist:
            pass
    return invitation