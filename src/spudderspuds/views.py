import re
from random import shuffle
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from google.appengine.api import blobstore
import simplejson
from spudderaccounts.models import Invitation
from spudderaccounts.templatetags.spudderaccountstags import is_fan, user_has_fan_role
from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleFan
from spudderaffiliates.models import Affiliate
from spudderdomain.controllers import TeamsController, RoleController, SpudsController, EntityController
from spudderdomain.models import FanPage, TeamPage, TeamAdministrator
from spudderkrowdio.models import FanFollowingEntityTag, KrowdIOStorage
from spuddersocialengine.models import SpudFromSocialMedia
from spudderspuds.challenges.utils import _AcceptAndPledgeEngineStates
from spudderspuds.forms import FanSigninForm, FanRegisterForm, FanPageForm, BasicSocialMediaForm
from spudderspuds.utils import create_and_activate_fan_role, is_signin_claiming_spud, set_social_media
from spudderspuds.decorators import can_edit
from spudmart.CERN.models import Student
from spudmart.CERN.rep import team_gained_follower, team_tagged_in_spud
from spudmart.accounts.templatetags.accounts import fan_page_name, user_name
from spudmart.sponsors.models import SponsorPage
from spudmart.upload.forms import UploadForm
from spudmart.upload.models import UploadedFile
from spudmart.utils.cover_image import reset_cover_image, save_cover_image_from_request
from spudderkrowdio.utils import start_following, stop_following, get_following, post_comment
from spudmart.venues.models import Venue
from spudderdomain.models import Challenge, ChallengeParticipation
from spudderdomain.wrappers import EntityBase


CHALLENGE_STATE_BUTTON = "<button class='btn btn-%s btn-xs pull-right' style='margin-right:5%%' title='%s'>%s</button>"
CHALLENGE_STATE_FORMATTING = {
    ChallengeParticipation.ACCEPTED_STATE: ('success',
                                            'You have accepted this challenge',
                                            'Accepted'),
    ChallengeParticipation.PRE_ACCEPTED_STATE: ('warning',
                                                'You have been invited to this challenge but haven\'t accepted yet',
                                                'Pre-Accepted'),
    ChallengeParticipation.DECLINED_STATE: ('danger',
                                            'You have declined this challenge',
                                            'Declined'),
    ChallengeParticipation.DONATE_ONLY_STATE: ('info',
                                               'You only donated to the team for this challenge',
                                               'Donated Only')

}

IMAGE = "<a class='btn btn-primary btn-xs challenge-image' title='Upload custom image' href='/challenges/%s/edit_image'>" \
        "<i class='fa fa-fw fa-camera'></i>" \
        "</a>"
DONATION = "<a class='btn btn-default btn-xs' title='Change suggested donations' href='/challenges/%s/edit_donation'>" \
           "<i class='fa fa-fw fa-usd'></i>" \
           "</a>"
SHARE_BUTTON = "<a class='btn btn-primary btn-xs' title='Share this Challenge' href='/challenges/%s/share'>" \
               "<i class='fa fa-fw fa-share-alt'></i>" \
               "</a>"
LINK = "<a class='btn btn-primary btn-xs' href='/challenges/%s'>" \
       "<i class='fa fa-fw fa-link'></i>" \
       "</a>"
# This definition is commented out because we don't have anywhere to upload videos currently
# VIDEO = "<a class='btn btn-default btn-xs' title='Add a custom video for this challenge'>" \
#         "<i class='fa fa-fw fa-video-camera text-primary'></i>" \
#         "</a>"
VIDEO = None


def _format_challenge_state_button(state):
    """
    Generates html for a button for the challenge state
    Used on the fan dashboard
    :param state: an value in ChallengeParticipation.STATES
    :return: a string with html for button
    """
    return CHALLENGE_STATE_BUTTON % CHALLENGE_STATE_FORMATTING[state]


def _get_icons(challenge, created):
    """
    Gets allowed icons for managing challenge
    :param challenge: a Challenge object
    :param created: a boolean whether to allow more than share button
    :return: a string of html objects:
        IMAGE or NO_IMAGE
        VIDEO or NO_VIDEO
        both are link tags with FontAwesome icon declarations
    """
    html = ""
    if created:
        html += IMAGE % challenge.id
        html += DONATION % challenge.id
    html += LINK % challenge.id
    html += SHARE_BUTTON % challenge.id
    return html


def _format_challenge(type, c, extras=None):
    if type == 'created':
        club = EntityController.GetWrappedEntityByTypeAndId(
            c.recipient_entity_type,
            c.recipient_entity_id,
            EntityBase.EntityWrapperByEntityType(c.recipient_entity_type))
        name = '%s for %s' % (c.name, club.name)
        return {
            'name': name,
            'link': '/challenges/%s' % c.id,
        }
    if type == 'waiting':
        club = EntityController.GetWrappedEntityByTypeAndId(
            c.challenge.recipient_entity_type,
            c.challenge.recipient_entity_id,
            EntityBase.EntityWrapperByEntityType(c.challenge.recipient_entity_type))
        return {
            'name': c.challenge.name,
            'link': '/challenges/%s/accept/notice' % c.challenge.id
        }
    if type == 'done':
        return {
            'name': 'Test'
        }
    if type == 'dash participating':
        club = EntityController.GetWrappedEntityByTypeAndId(
            c.challenge.recipient_entity_type,
            c.challenge.recipient_entity_id,
            EntityBase.EntityWrapperByEntityType(c.challenge.recipient_entity_type))
        created = c.challenge.creator_entity_id == extras['id'] and c.challenge.creator_entity_type == extras['type']
        return {
            'name': "%s for %s" % (c.challenge.name, club.name),
            'link': c.link(),
            'state': _format_challenge_state_button(c.state),
            'manage': _get_icons(c.challenge, created)
        }
    if type == 'dash created' and c.id not in extras:
        club = EntityController.GetWrappedEntityByTypeAndId(
            c.recipient_entity_type,
            c.recipient_entity_id,
            EntityBase.EntityWrapperByEntityType(c.recipient_entity_type))
        return {
            'name': "%s for %s" % (c.name, club.name),
            'link': '/challenges/%s' % c.id,
            'state': '',
            'manage': _get_icons(c, True)
        }


def landing_page(request):
    template_data = {
        'find_teams': TeamPage.objects.all()[:10],
        'find_fans': FanPage.objects.all()[:10],
        'find_venues': Venue.objects.all()[:10]}
    if is_fan(request.current_role):
        spud_stream = SpudsController(request.current_role).get_spud_stream()
        fan_spuds = SpudsController.GetSpudsForFan(request.current_role.entity)
        stream = SpudsController.MergeSpudLists(spud_stream, fan_spuds)
        template_data['spuds'] = stream

        entity = {
            'id': request.current_role.entity.id,
            'type': request.current_role.entity_type
        }

        participating_challenges = ChallengeParticipation.objects.filter(
            participating_entity_id=entity['id'],
            participating_entity_type=entity['type'])
        template_data['challenge_participations'] = participating_challenges
        template_data['accept_and_pledge_states'] = _AcceptAndPledgeEngineStates

        participating_ids = [c.challenge.id for c in participating_challenges]

        template_data['challenges'] = [_format_challenge('dash participating', c, entity)
                                       for c in participating_challenges] + \
                                      [_format_challenge('dash created', c, participating_ids)
                                       for c in Challenge.objects.filter(creator_entity_id=entity['id'],
                                                                         creator_entity_type=entity['type'])]

        template_data['fan_nav_active'] = "explore"
    return render(request, 'spudderspuds/pages/landing_page.html', template_data)


def entity_search(request, entity_type):
    template_data = {'entity_type': entity_type}
    if entity_type == "fan":
        fans = FanPage.objects
        template_data['entities'] = fans.exclude(fan=request.user) if request.current_role else fans.all()
    if entity_type == "team":
        template_data['entities'] = TeamPage.objects.all()
    if entity_type == "venue":
        template_data['entities'] = Venue.objects.all()
    return render(request, 'spudderspuds/pages/entity_search.html', template_data)


def fan_signin(request):
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_FAN:
        return redirect('/spuds')
    template_data = {}
    if request.method == "POST":
        form = FanSigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email_address')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            fan = FanPage.objects.filter(fan=user)[0]
            change_current_role(request, RoleController.ENTITY_FAN, fan.id)
            is_signin_claiming_spud(
                request,
                fan,
                form.cleaned_data.get('twitter', None),
                form.cleaned_data.get('spud_id', None))
            redirect_to = request.session.pop('redirect_after_auth', '/spuds')
            return redirect(redirect_to)
    else:
        form = FanSigninForm(initial=request.GET)
    template_data["form"] = form
    return render_to_response(
        'spudderspuds/pages/user_signin.html',
        template_data,
        context_instance=RequestContext(request))


def fan_register(request):
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_FAN:
        return redirect('/spuds')
    if request.current_role and not is_fan(request.current_role) and not user_has_fan_role(request):
        if request.GET.get('twitter', None) and request.GET.get('spud_id', None):
            return redirect(
                '/spuds/register_add_fan_role?twitter=%s&spud_id=%s' %
                (request.GET['twitter'], request.GET['spud_id']))
        else:
            return redirect('/spuds/register_add_fan_role')

    invitation_id = request.session.get('invitation_id')
    invitation = None
    if invitation_id:
        try:
            invitation = Invitation.objects.get(id=invitation_id, status=Invitation.PENDING_STATUS)
        except Invitation.DoesNotExist:
            pass


    template_data = {}
    if request.method == "POST":
        form = FanRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email_address')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username, username, password)
            user.save()
            user.spudder_user.mark_password_as_done()
            fan_role = create_and_activate_fan_role(request, user)
            login(request, authenticate(username=username, password=password))
            is_signin_claiming_spud(
                request,
                fan_role.entity,
                form.cleaned_data.get('twitter', None),
                form.cleaned_data.get('spud_id', None))
            if invitation:
                if invitation.invitation_type == Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION:
                    team_admin = TeamAdministrator(entity_type=fan_role.entity_type, entity_id=fan_role.entity.id)
                    team_admin.team_page_id = invitation.target_entity_id
                    team_admin.save()
                    invitation.status = Invitation.ACCEPTED_STATUS
                    invitation.save()
                elif invitation.invitation_type == Invitation.AFFILIATE_INVITE_CLUB_ADMINISTRATOR:
                    fan_role.entity.affiliate = Affiliate.objects.get(name=invitation.extras['affiliate_name'])
                    return HttpResponseRedirect('/spudderaffiliates/invitation/%s/create_club' % invitation.id)
                return redirect('/fan/follow?origin=invitation')
            return redirect('/fan/%s/edit?new_registration=true' % fan_role.entity.id)
    else:
        form = FanRegisterForm(initial=request.GET)
    template_data["form"] = form
    return render_to_response(
        'spudderspuds/pages/user_register.html',
        template_data,
        context_instance=RequestContext(request))


def user_add_fan_role(request):
    if not request.current_role:
        return redirect('/spuds/register')
    fan_role = create_and_activate_fan_role(request, request.user)
    return redirect('/fan/%s/edit?new_registration=true' % fan_role.entity.id)


def fan_profile_view(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    fan_role = RoleFan(page)
    krowdio_response = get_following(fan_role)
    template_data = {
        'page': page,
        'role': fan_role,
        'fan_spuds': SpudsController.GetSpudsForFan(page),
        'base_url': 'spudderspuds/base.html',
        'following_teams': krowdio_users_to_links(request.can_edit,
                                                  fan_role,
                                                  krowdio_response['data'],
                                                  EntityController.ENTITY_TEAM),
        'following_fans': krowdio_users_to_links(request.can_edit,
                                                 fan_role,
                                                 krowdio_response['data'],
                                                 RoleController.ENTITY_FAN)
    }
    if request.can_edit:
        template_data['following_teams_title'] = "<img src='/static/img/spudderspuds/button-teams-tiny.png' /> Teams You Follow"
        template_data['following_fans_title'] = "<img src='/static/img/spudderspuds/button-fans-tiny.png' /> Fans You Follow"
    else:
        template_data['following_teams_title'] = "<img src='/static/img/spudderspuds/button-teams-tiny.png' /> Teams %s Follows" % page.name
        template_data['following_fans_title'] = "<img src='/static/img/spudderspuds/button-fans-tiny.png' /> Fans %s Follows" % page.name

    template_data['fan_nav_active'] = 'profile'
    template_data['challenges'] = {
        'created': [_format_challenge('created', c) for c in Challenge.objects.filter(
            creator_entity_id=fan_role.entity.id,
            creator_entity_type=RoleController.ENTITY_FAN)],
        'waiting': [_format_challenge('waiting', c) for c in ChallengeParticipation.objects.filter(
            participating_entity_id=fan_role.entity.id,
            participating_entity_type=RoleController.ENTITY_FAN,
            state=ChallengeParticipation.PRE_ACCEPTED_STATE).select_related('challenge')]
    }
    return render(request, 'spudderspuds/fans/pages/fan_page_view.html', template_data)


@can_edit
def fan_profile_edit(request, page_id):
    fan_page = get_object_or_404(FanPage, pk=page_id)
    profile_form = FanPageForm(initial=fan_page.__dict__, image=fan_page.avatar)
    social_accounts_form = BasicSocialMediaForm(initial=fan_page.__dict__)
    if request.method == 'POST':
        profile_form = FanPageForm(request.POST, image=fan_page.avatar)
        social_accounts_form = BasicSocialMediaForm(request.POST)
        if profile_form.is_valid() and social_accounts_form.is_valid():
            for attr in ('name', 'date_of_birth', 'state', ):
                fan_page.__setattr__(attr, profile_form.cleaned_data[attr])

            set_social_media(fan_page, social_accounts_form)

            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                fan_page.avatar = upload_form.save()

            fan_page.save()
        redirect_to = request.session.pop('redirect_after_auth', '/fan/%s' % fan_page.id)
        return redirect(redirect_to)
    return render(request, 'spudderspuds/fans/pages/fan_page_edit.html', {
        'profile_form': profile_form,
        'social_accounts_form': social_accounts_form,
        'page': fan_page,
        'new_registration': request.GET.get('new_registration', False),
        'upload_url': blobstore.create_upload_url('/fan/%s/edit' % page_id)
    })


def fan_profile_save_avatar(request, page_id):
    avatar_id = request.POST['avatar'].split('/')[3]
    avatar = get_object_or_404(UploadedFile, pk=avatar_id)

    page = get_object_or_404(FanPage, pk=page_id)
    page.avatar = avatar
    page.save()

    return HttpResponse('ok')


def fan_profile_edit_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': 'Fan Page',
        'return_url': "/fan/%s" % page.id,
        'post_url': '/fan/%s/save_cover' % page.id,
        'reset_url': '/fan/%s/reset_cover' % page.id
    })


def fan_profile_reset_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    reset_cover_image(page)

    return HttpResponse('OK')


def fan_profile_save_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    save_cover_image_from_request(page, request)

    return HttpResponse()


def fan_my_teams(request, page_id):
    template_data = {
        'teams': TeamsController.TeamsAdministeredByRole(request.current_role),
        'role_dashboard': 'spudderspuds/base.html',
        'fan_nav_active': 'teams',
        'info_message_id': 'teams_list',
        'info_message_url': '/fan/disable_about/'
    }
    return render(request, 'components/sharedpages/teams/teams_list.html', template_data,
                  context_instance=RequestContext(request))


def disable_about(request):
    """
    Disables 'about X' part of given page for given fan
    """
    if request.method == 'POST':
        fan = request.current_role.entity
        message_id = request.POST.get('message_id')
        if message_id:
            fan.dismiss_info_message(message_id)
        return HttpResponse(fan.info_messages_dismissed)
    else:
        return HttpResponseNotAllowed(['POST'])


def claim_atpostspud(request, spud_id):
    try:
        spud = SpudFromSocialMedia.objects.get(id=spud_id)
    except SpudFromSocialMedia.DoesNotExist:
        spud = None
    if spud.state == SpudFromSocialMedia.STATE_ACCEPTED:  # Don't allow dupes!
        spud = None
    template_data = {
        'spud': spud.expanded_data if spud else None,
        'spud_id': spud.id if spud else None
    }
    if request.method == "POST":
        action = request.POST.get('action', None)
        if action == "change_twitter" or action == "set_twitter":
            new_username = spud.expanded_data['user']['username']
            fan = request.current_role.entity
            fan.twitter = new_username
            fan.save()
            controller = SpudsController(request.current_role)
            controller.add_spud_from_fan(spud)
            template_data['username_changed'] = action == "change_twitter"
            template_data['username_set'] = action == "set_twitter"
    return render_to_response(
        'spudderspuds/pages/claim_atpostspud.html',
        template_data,
        context_instance=RequestContext(request))


def follow(request):
    """
    A page allowing the Fan to create a custom #tag for entity
    :param request: a GET request
    :return: a single well with form for entity #tag, or an
        HTTPResponseNotAllowed
    """
    if request.method == 'GET':
        origin = str(request.GET.get('origin', ''))
        name = tag = base_well_url = base_quote_url = None
        fan_tags = FanFollowingEntityTag.objects.filter(fan=request.current_role.entity)

        if re.match(r'/venues/view/\d+', origin):
            ven = Venue.objects.get(id=str.split(origin, '/')[-1])
            name = ven.aka_name
            tag = ven.name
            base_well_url = 'spuddercern/base_single_well.html'
            base_quote_url = 'spuddercern/quote_messages/base_quote_message.html'

        elif re.match(r'/fan/\d+', origin):
            fan = FanPage.objects.get(id=str.split(origin, '/')[-1])
            name = fan_page_name(fan)
            tag = name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'

        elif re.match(r'/team/\d+/admins', origin):
            team = TeamPage.objects.get(id=str.split(origin, '/')[2])
            name = team.name
            tag = team.at_name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'
            origin = "/team/%s" % team.id
            messages.success(
                request,
                "<h4><i class='fa fa-check'></i> You accepted the invitation to become an administrator</h4>"
                "<p>You are now and administrator of %s, please create a custom #tag</p>" % team.name)

        elif re.match(r'/team/\d+', origin):
            team = TeamPage.objects.get(id=str.split(origin, '/')[-1])
            name = team.name
            tag = team.at_name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'

        elif re.match(r'/team/create', origin):
            team = TeamPage.objects.get(id=request.GET.get('team_id'))
            name = team.name
            tag = team.at_name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'
            origin = "/team/%s" % team.id
            messages.success(
                request,
                "<h4><i class='fa fa-check'></i> Team %s successfully created!</h4>"
                "<p>You successfully create your new team, now please give them a custom #tag</p>" % team.name)

        elif origin == 'invitation':
            invitation_id = request.session.get('invitation_id')
            if invitation_id:
                origin = '/fan/%s/edit?new_registration=true' % request.current_role.entity.id
                try:
                    invitation = Invitation.objects.get(id=invitation_id)
                    if invitation.invitation_type == Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION:
                        team = TeamPage.objects.get(id=invitation.target_entity_id)
                        name = team.name
                        tag = team.at_name
                        base_well_url = 'spudderspuds/base_single_well.html'
                        base_quote_url = 'spudderspuds/components/base_quote_message.html'
                        messages.success(
                            request,
                            "<h4><i class='fa fa-check'></i> You accepted the invitation to become an administrator</h4>"
                            "<p>You are now and administrator of %s, please create a custom #tag</p>" % team.name)
                    else:
                        raise Invitation.DoesNotExist()
                except Invitation.DoesNotExist:
                    return HttpResponseRedirect(origin)

        template_data = {
            'name': name,
            'tag': tag,
            'base_well_url': base_well_url,
            'base_quote_url': base_quote_url,
            'origin': origin,
            'fan_tags': fan_tags}
        return render(request, 'components/sharedpages/following/start_following.html', template_data)

    else:
        return HttpResponseNotAllowed(['GET'])


def start_following_view(request):
    """
    Current role (fan) starts following entity in request
    :param request: a POST request
    :return: the response from the KrowdIO API on success,
        or an HttpResponseNotAllowed response
    """
    if request.method == 'POST':
        origin = str(request.POST.get('origin', ''))
        entity_id = entity_type = None
        tag = str(request.POST.get('tag', None)) or request.POST['base_tag']  # if empty use the entity name
        if re.match(r'/venues/view/\d+', origin):
            entity_type = EntityController.ENTITY_VENUE
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/fan/\d+/edit', origin):
            invitation_id = request.session.pop('invitation_id')
            if invitation_id:
                try:
                    invitation = Invitation.objects.get(id=invitation_id)
                    if invitation.invitation_type == Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION:
                        entity_id = invitation.target_entity_id
                        entity_type = EntityController.ENTITY_TEAM
                    else:
                        raise Invitation.DoesNotExist()
                except Invitation.DoesNotExist:
                    return HttpResponseBadRequest()
        elif re.match(r'/fan/\d+', origin):
            entity_type = RoleController.ENTITY_FAN
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/team/\d+', origin):
            entity_type = EntityController.ENTITY_TEAM
            entity_id = str.split(origin, '/')[2]
            team = TeamPage.objects.get(id=entity_id)
            admin = TeamAdministrator.objects.get(team_page=team,
                                                  entity_id=request.current_role.entity.id,
                                                  entity_type=request.current_role.entity_type)
            if admin.entity_type == 'student':
                stu = Student.objects.get(id=admin.entity_id)
                team_gained_follower(stu)

        entity_tag = FanFollowingEntityTag(
            fan=request.current_role.entity,
            tag=tag,
            entity_id=entity_id,
            entity_type=entity_type)
        entity_tag.save()

        json = start_following(request.current_role, entity_type, entity_id)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])


def stop_following_view(request):
    """
    Current role (fan) stops following entity in request
    :param request: a POST request
    :return: the response from the KrowdIO API on success,
        or an HttpResponseNotAllowed response
    """
    if request.method == 'POST':
        origin = str(request.POST.get('origin', ''))
        entity_id = entity_type = None
        if re.match(r'/venues/view/\d+', origin):
            entity_type = EntityController.ENTITY_VENUE
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/fan/\d+', origin):
            entity_type = RoleController.ENTITY_FAN
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/team/\d+', origin):
            entity_type = EntityController.ENTITY_TEAM
            entity_id = str.split(origin, '/')[-1]

        fan_tag = FanFollowingEntityTag.objects.get(
            fan=request.current_role.entity,
            entity_type=entity_type,
            entity_id=entity_id)
        fan_tag.delete()

        json = stop_following(request.current_role, entity_type, entity_id)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])


def krowdio_users_to_links(can_edit, current_role, krowdio_dict, filter=None):
    """
    Translates KrowdIO users into a list of dicts about Spudder entities
    :param krowdio_dict: the 'users' part of a response from the
        KrowdIO API (intended for use with followers/following)
    :return: a list of dicts, where the dict contains the icon link,
        profile link, and name of each Spudder entity followed
    """
    users = []
    for user in krowdio_dict:
        krowdio_id = user['_id']
        try:
            storage_obj = KrowdIOStorage.objects.get(krowdio_user_id=krowdio_id)
        except KrowdIOStorage.DoesNotExist:
            continue

        if storage_obj.role_type == RoleController.ENTITY_FAN and \
                (filter == RoleController.ENTITY_FAN or filter is None):
            fan = FanPage.objects.get(id=storage_obj.role_id)
            if fan.avatar:
                icon_link = '/file/serve/%s' % fan.avatar.id
            else:
                icon_link = '/static/img/spudderfans/button-fans-tiny.png'
            users.append({
                'name': fan.name,
                'profile': '/fan/%s' % fan.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=fan.id,
                    entity_type=RoleController.ENTITY_FAN) if can_edit else None
            })
        elif storage_obj.role_type == RoleController.ENTITY_SPONSOR and \
                (filter == RoleController.ENTITY_SPONSOR or filter is None):
            sponsor = SponsorPage.objects.get(id=storage_obj.role_id)
            if sponsor.thumbnail:
                icon_link = '/file/serve/%s' % sponsor.thumbnail
            else:
                icon_link = '/static/img/spuddersponsors/button-sponsors-tiny.png'
            users.append({
                'name': sponsor.name,
                'profile': '/sponsor/%s' % sponsor.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=sponsor.id,
                    entity_type=RoleController.ENTITY_SPONSOR) if can_edit else None
            })
        elif storage_obj.role_type == RoleController.ENTITY_STUDENT and \
                (filter == RoleController.ENTITY_STUDENT or filter is None):
            stu = Student.objects.get(id=storage_obj.role_id)
            if stu.logo:
                icon_link = '/file/serve/%s' % stu.logo
            else:
                icon_link = 'static/img/spuddercern/button-cern-tiny.png'
            users.append({
                'name': user_name(stu.user),
                'profile': '/cern/student/%s' % stu.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=stu.id,
                    entity_type=RoleController.ENTITY_STUDENT) if can_edit else None
            })
        elif storage_obj.venue and \
                (filter == EntityController.ENTITY_VENUE or filter is None):
            if storage_obj.venue.logo:
                icon_link = '/file/serve/%s' % storage_obj.venue.logo.id
            else:
                icon_link = '/static/img/spudderspuds/button-spuds-tiny.png'
            users.append({
                'name': storage_obj.venue.aka_name,
                'profile': '/venues/view/%s' % storage_obj.venue.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=storage_obj.venue.id,
                    entity_type=EntityController.ENTITY_VENUE) if can_edit else None
            })
        elif storage_obj.team and \
                (filter == EntityController.ENTITY_TEAM or filter is None):

            if storage_obj.team.image:
                icon_link = '/file/serve/%s' % storage_obj.team.image.id
            else:
                icon_link = '/static/img/spudderspuds/button-teams-tiny.png'
            users.append({
                'name': storage_obj.team.name,
                'profile': '/team/%s' % storage_obj.team.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=storage_obj.team.id,
                    entity_type=EntityController.ENTITY_TEAM) if can_edit else None
            })
    return users


def test_spuds(request):
    template_data = {}
    if is_fan(request.current_role):
        stream = SpudsController(request.current_role).get_spud_stream() + SpudsController.GetSpudsForFan(
            request.current_role.entity)
        # shuffle(stream)
        template_data['spuds'] = stream
        return render(request, 'spudderspuds/pages/test_spuds.html', template_data)


def add_spud_comment(request):
    """
    Adds a comment to a SPUD (KrowdIO post) that tags Spudder entities
    :param request: a POST request
    :return: response from KrowdIO or HttpResponseNotAllowed
    """
    if request.method == 'POST':
        entity = KrowdIOStorage.GetOrCreateForCurrentUserRole(
            user_role=request.current_role)
        spud_id = request.POST.get('spud_id')
        tags = request.POST.getlist('tags[]')

        text = ""
        fan = request.current_role.entity
        for t in tags:
            tag = FanFollowingEntityTag.objects.get(fan=fan, tag=t)
            text += "@%s%s " % (tag.entity_type, tag.entity_id)
            if tag.entity_type == 'Team':
                team = TeamPage.objects.get(id=tag.entity_id)
                admin = TeamAdministrator.objects.get(team_page=team)
                if admin.entity_type == 'student':
                    stu = Student.objects.get(id=admin.entity_id)
                    team_tagged_in_spud(stu)

        json = post_comment(entity, spud_id, text)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])


def get_at_names(request):
    """
    Gets all the currently used @names
    :param request: a POST request
    :return: a list of strings
    """
    at_names = []
    for v in Venue.objects.all().exclude(name="VenueTagName"):
        at_names.append(v.name)
    for s in SponsorPage.objects.all():
        at_names.append(s.tag)
    for t in TeamPage.objects.all().exclude(at_name=None):
        at_names.append(t.at_name)

    return HttpResponse(simplejson.dumps(at_names))
