from google.appengine.api import mail
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from google.appengine.api import blobstore
import re
import settings
from spudderaccounts.controllers import InvitationController
from spudderaccounts.models import Invitation
from spudderaccounts.templatetags.spudderaccountstags import is_fan, is_cern_student
from spudderaccounts.wrappers import RoleBase
from spudderdomain.controllers import TeamsController, RoleController, SpudsController, SocialController, \
    EntityController
from spudderdomain.models import TeamPage, Location, TeamVenueAssociation, TeamAdministrator, FanPage
from spudderdomain.wrappers import EntityBase
from spudderspuds.forms import LinkedInSocialMediaForm
from spudderspuds.utils import set_social_media
from spudderspuds.decorators import can_edit
from spudmart.CERN.rep import created_team, team_associated_with_venue
from spudmart.teams.forms import CreateTeamForm, TeamPageForm, EditTeamForm, InviteNewFanByEmailForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, \
    HttpResponseBadRequest
from spudmart.upload.models import UploadedFile
from spudmart.upload.forms import UploadForm
from spudmart.utils.Paginator import EntitiesPaginator
from spudmart.utils.cover_image import save_cover_image_from_request, reset_cover_image
from spudmart.CERN.models import STATES, Student
from spudmart.utils.url import get_return_url
from spudmart.venues.models import SPORTS, Venue


def teams_list(request):
    template_data = {
        'teams': TeamsController.TeamsAdministeredByRole(request.current_role),
        'role_dashboard': '',
        'info_message_id': 'teams_list'
    }

    if request.current_role.entity_type == RoleController.ENTITY_STUDENT:
        template_data['role_dashboard'] = 'spuddercern/pages/dashboard_pages/dashboard.html'
        template_data['info_message_url'] = '/cern/disable_about/'
    elif request.current_role.entity_type == RoleController.ENTITY_FAN:
        template_data['role_dashboard'] = 'spudderspuds/fans/pages/dashboard.html'
        template_data['fan_nav_active'] = 'teams'
        template_data['info_message_url'] = '/fan/disable_about/'
    return render(request, 'components/sharedpages/teams/teams_list.html',
                  template_data)


def create_team(request):
    form = CreateTeamForm(initial={'next_url': request.GET.get('next_url')})
    social_media_form = LinkedInSocialMediaForm()
    template_data = {'SPORTS': SPORTS}
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        social_media_form = LinkedInSocialMediaForm(request.POST)

        if form.is_valid() and social_media_form.is_valid():
            team = TeamsController.CreateTeam(
                request.current_role,
                name=form.cleaned_data.get('name'),
                contact_details=form.cleaned_data.get('contact_details'),
                free_text=form.cleaned_data.get('free_text'),
                sport=dict(form.fields['sport'].choices)[form.cleaned_data.get('sport')],
                state=form.cleaned_data.get('state'),
                at_name=form.cleaned_data.get('at_name'),
            )

            location_info = request.POST.get('location_info', None)
            team.update_location(location_info)

            set_social_media(team, social_media_form)

            team.save()
            if is_fan(request.current_role):
                redirect_url = "/fan/follow?origin=/team/create&team_id=%s" % team.id
            else:
                if is_cern_student(request.current_role):
                    created_team(request.current_role.entity)
                redirect_url = "/team/%s" % team.id

            return redirect(redirect_url)

    template_data['form'] = form
    template_data['social_media'] = social_media_form
    return render(request, 'spudderspuds/teams/pages/create_team.html', template_data)


def _update_team_page_location(page, location):
    if location:
        if not page.location:
            page.location = Location.from_post_data(location)
        else:
            page.location.update_from_post_data(location)
    else:
        page.location = None


def team_page(request, page_id):
    page = TeamPage.objects.get(pk=page_id)
    social_media_form = LinkedInSocialMediaForm(initial=page.__dict__)

    if request.method == 'POST':
        form = TeamPageForm(request.POST, instance=page)
        social_media_form = LinkedInSocialMediaForm(request.POST)

        if form.is_valid() and social_media_form.is_valid():
            updated_page = form.save(commit=False)

            location_info = request.POST['location_info']
            updated_page.update_location(location_info)

            set_social_media(page, social_media_form)

            updated_page.save()

            return HttpResponseRedirect('/team/page/%s' % page_id)

    form = TeamPageForm(instance=page)

    return render(request, 'spudderspuds/teams/pages/dashboard_pages/team_page_edit.html', {
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'page': page,
        'form': form,
        'social_media': social_media_form,
        'sports': SPORTS,
        'states': sorted([(k, v) for k, v in STATES.items()], key=lambda x: x[1])
    })


@can_edit()
def edit_team_page(request, page_id):
    team_page = TeamPage.objects.select_related('image').get(pk=page_id)
    form = EditTeamForm(initial=team_page.__dict__, image=team_page.image)

    if request.method == 'POST':
        form = EditTeamForm(request.POST, team_id=team_page.id, image=team_page.image)

        if form.is_valid():

            upload_form = UploadForm(request.POST, request.FILES)
            uploaded_file_model = None
            if upload_form.is_valid():
                uploaded_file_model = upload_form.save()

            data = form.cleaned_data
            team_page.name = data.get('name')
            team_page.contact_details = data.get('contact_details')
            team_page.free_text = data.get('free_text')
            if uploaded_file_model:
                team_page.image = uploaded_file_model
            team_page.save()
            return HttpResponseRedirect('/team/%s' % page_id)

    return render(request, 'spudderspuds/teams/pages/edit_team.html', {
        'page': team_page,
        'form': form,
        'upload_url': blobstore.create_upload_url('/team/%s/edit' % page_id)
    })


@can_edit()
def manage_team_page_admins(request, page_id):
    team_page = get_object_or_404(TeamPage, pk=page_id)
    # get current team admins
    team_admins_ids = TeamAdministrator.objects\
        .filter(team_page=team_page, entity_type=RoleController.ENTITY_FAN).values_list('entity_id', flat=True)
    team_admins_ids = [int(fan_id) for fan_id in team_admins_ids]
    admins = FanPage.objects.filter(id__in=team_admins_ids)
    # get invited fans
    invited_fans_ids = Invitation.objects.filter(
        invitee_entity_type=RoleController.ENTITY_FAN,
        invitation_type=Invitation.ADMINISTRATE_TEAM_INVITATION,
        status=Invitation.PENDING_STATUS,
        target_entity_id=team_page.id,
        target_entity_type=EntityController.ENTITY_TEAM
    ).values_list('invitee_entity_id', flat=True)
    invited_fans_ids = [int(fan_id) for fan_id in invited_fans_ids]
    invited_fans = FanPage.objects.filter(id__in=invited_fans_ids)
    # get not invited fans
    not_invited_ids = list(team_admins_ids) + list(invited_fans_ids)
    not_invited_fans = FanPage.objects.exclude(id__in=not_invited_ids)
    form = InviteNewFanByEmailForm(team_id=team_page.id)
    is_form_sent = False
    # get invited non-users
    invited_non_users = Invitation.objects.filter(
        invitation_type=Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION,
        status=Invitation.PENDING_STATUS,
        target_entity_id=team_page.id,
        target_entity_type=EntityController.ENTITY_TEAM
    ).order_by('-modified')

    if request.method == 'POST':
        form = InviteNewFanByEmailForm(request.POST, team_id=team_page.id)
        if form.is_valid():
            is_form_sent = True
            InvitationController.InviteNonUser(
                form.cleaned_data['email'], Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION,
                team_page.id, EntityController.ENTITY_TEAM)
            form = InviteNewFanByEmailForm(team_id=team_page.id)

    return render(request, 'spudderspuds/teams/pages/manage_team_admins.html', {
        'page': team_page,
        'admins': admins,
        'invited_fans': invited_fans,
        'not_invited_fans': not_invited_fans,
        'invited_non_users': invited_non_users,
        'form': form,
        'is_form_sent': is_form_sent
    })


@can_edit()
@require_http_methods(["GET", "POST"])
def create_fan_invitation(request, page_id, fan_id):
    entity_team = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_TEAM, page_id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_TEAM))
    fan = get_object_or_404(FanPage, pk=fan_id)

    # check that fan is not an admin already
    if entity_team.is_admin(fan.id, RoleController.ENTITY_FAN):
        return HttpResponseBadRequest()

    if request.method == 'GET':
        return render(request, 'spudderspuds/teams/pages/create_fan_invitation.html', {
            'team_page': entity_team.entity,
            'fan': fan
        })
    elif request.method == 'POST':
        InvitationController.InviteEntity(
            fan.id, RoleController.ENTITY_FAN, Invitation.ADMINISTRATE_TEAM_INVITATION,
            entity_team.entity.id, entity_team.entity_type)
        return HttpResponseRedirect('/team/%s/admins' % page_id)


@can_edit()
@require_http_methods(["GET", "POST"])
def cancel_fan_invitation(request, page_id, fan_id):
    entity_team = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_TEAM, page_id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_TEAM))
    fan = get_object_or_404(FanPage, pk=fan_id)

    # check that fan is not an admin already
    if entity_team.is_admin(fan.id, RoleController.ENTITY_FAN):
        return HttpResponseBadRequest()

    if request.method == 'GET':
        return render(request, 'spudderspuds/teams/pages/cancel_fan_invitation.html', {
            'team_page': team_page,
            'fan': fan
        })
    elif request.method == 'POST':
        InvitationController.CancelEntityInvitation(
            fan.id, RoleController.ENTITY_FAN, Invitation.ADMINISTRATE_TEAM_INVITATION,
            entity_team.entity.id, entity_team.entity_type)
        return HttpResponseRedirect('/team/%s/admins' % page_id)


@can_edit()
@require_http_methods(["GET", "POST"])
def revoke_fan_invitation(request, page_id, fan_id):
    entity_team = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_TEAM, page_id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_TEAM))
    fan = get_object_or_404(FanPage, pk=fan_id)

    # check that fan is an admin
    if not entity_team.is_admin(fan.id, RoleController.ENTITY_FAN):
        return HttpResponseBadRequest()

    if request.method == 'GET':
        return render(request, 'spudderspuds/teams/pages/revoke_fan_invitation.html', {
            'team_page': entity_team.entity,
            'fan': fan
        })
    if request.method == 'POST':
        InvitationController.RevokeEntityInvitation(
            fan.id, RoleController.ENTITY_FAN, Invitation.ADMINISTRATE_TEAM_INVITATION,
            entity_team.entity.id, entity_team.entity_type)
        return HttpResponseRedirect('/team/%s/admins' % page_id)


@require_http_methods(["GET", "POST"])
def accept_fan_invitation(request, page_id, invitation_id):
    entity_team = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_TEAM, page_id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_TEAM))
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    fan = get_object_or_404(FanPage, pk=invitation.invitee_entity_id)
    if request.user != fan.fan:
        return HttpResponseBadRequest()

    # check that fan is not an admin already
    if entity_team.is_admin(fan.id, RoleController.ENTITY_FAN):
        return HttpResponseBadRequest()

    if request.method == 'GET':
        return render(request, 'spudderspuds/teams/pages/accept_fan_invitation.html', {
            'team_page': entity_team.entity,
            'fan': fan,
            'invitation': invitation,
            'is_invitation_active': invitation.status == invitation.PENDING_STATUS
        })
    if request.method == 'POST':
        invitation.status = Invitation.ACCEPTED_STATUS
        invitation.save()
        team_admin = TeamAdministrator(
            entity_type=RoleController.ENTITY_FAN,
            entity_id=fan.id,
            team_page=entity_team.entity
        )
        team_admin.save()
        if SocialController.IsFanFollowsTheTeam(fan, entity_team.entity):
            return HttpResponseRedirect('/team/%s/admins' % page_id)
        else:
            redirect_url = "/fan/follow?origin=/team/%s/admins" % entity_team.entity.id
            return HttpResponseRedirect(redirect_url)


def public_view(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    is_associated, associated_venues = _check_if_team_is_associated(page)
    template_data = {
        'page': page,
        'is_associated': is_associated,
        'venues': associated_venues,
        'base_url': 'spudderspuds/base.html',
        'team_spuds': SpudsController.GetSpudsForTeam(page)}

    return render(request, 'spudderspuds/teams/pages/team_page_view.html', template_data)


def save_avatar(request, page_id):
    avatar_id = request.POST['avatar'].split('/')[3]
    avatar = get_object_or_404(UploadedFile, pk=avatar_id)

    page = get_object_or_404(TeamPage, pk=page_id)
    page.image = avatar
    page.save()

    return HttpResponse('ok')


def search_teams(request):
    filters = {}
    state = request.GET.get('state', None)
    sport = request.GET.get('sport', None)
    if state or sport:
        filters['state']= state
        filters['sport'] = sport
        teams = TeamPage.objects.filter(sport = sport, state = state)
    else:
        teams = TeamPage.objects.all()
    context = {
        'teams': teams,
        'sports': SPORTS,
        'states': STATES,
        'filters': filters
    }
    return render(request, 'spudderspuds/teams/pages/search_teams.html', context)
    

def edit_cover(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': 'Fan Page',
        'return_url': "/team/%s" % page.id,
        'post_url': '/team/%s/save_cover' % page.id,
        'reset_url': '/team/%s/reset_cover' % page.id
    })


def save_cover(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    save_cover_image_from_request(page, request)

    return HttpResponse()


def reset_cover(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    reset_cover_image(page)

    return HttpResponse('OK')


def remove_image(request):
    page = TeamPage.objects.get(team = request.user)
    page.image = None
    page.save()
    return HttpResponse('ok')


def _check_if_team_is_associated(page):
    is_associated = TeamVenueAssociation.objects.filter(team_page=page).count() > 0
    associated_venues = []

    if is_associated:
        for association in TeamVenueAssociation.objects.filter(team_page=page):
            associated_venues.append(association.venue)

    return is_associated, associated_venues


def associate_with_venue(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    venues_objects = Venue.objects.filter(sport=page.sport).order_by('name')
    is_associated, associated_venues = _check_if_team_is_associated(page)
    venues = []

    for venue in venues_objects:
        if venue not in associated_venues:
            venues.append(venue)


    # Pagination
    current_page = int(request.GET.get('page',1))
    venues_paginator = EntitiesPaginator(venues, 20)
    venue_page = venues_paginator.page(current_page)

    role_dashboard = 'spudderspuds/teams/pages/dashboard_pages/dashboard_base.html'
    if request.current_role.entity_type == RoleController.ENTITY_STUDENT:
        role_dashboard = 'spuddercern/pages/dashboard_pages/dashboard.html'
    elif request.current_role.entity_type == RoleController.ENTITY_FAN:
        role_dashboard = 'spudderspuds/fans/pages/dashboard.html'

    return render(request, 'components/sharedpages/teams/associate_with_venue.html', {
        'page': page,
        'venues': venue_page.object_list,
        'total_pages': venues_paginator.num_pages,
        'paginator_page': venue_page.number,
        'start': venue_page.start_index(),
        'role_dashboard': role_dashboard,
    })


def remove_association_with_venue(request, page_id, venue_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    venue = get_object_or_404(Venue, pk=venue_id)
    TeamVenueAssociation.objects.get(team_page=page, venue=venue).delete()

    return HttpResponseRedirect(get_return_url(request, '/team/%s' % page_id))


def associate_team_with_venue(request, page_id, venue_id):
    team = get_object_or_404(TeamPage, pk=page_id)
    venue = get_object_or_404(Venue, pk=venue_id)
    TeamVenueAssociation.objects.get_or_create(team_page=team, venue=venue)[0].save()
    SocialController.AssociateTeamWithVenue(team, venue)
    admin = TeamAdministrator.objects.get(team_page=team)
    if admin.entity_type == 'student':
        stu = Student.objects.get(id=admin.entity_id)
        team_associated_with_venue(stu)
    return HttpResponseRedirect('/team/%s' % page_id)


def disable_about(request):
    if request.method == 'POST':
        team = request.current_role.entity
        message_id = request.POST.get('message_id')
        if message_id:
            team.dismiss_info_message(message_id)
        return HttpResponse(team.info_messages_dismissed)
    else:
        return HttpResponseNotAllowed(['POST'])


def send_message(request, page_id):
    """
    Sends a message to the team manager
    :param request: a POST request with message body
    :param team_id: a valid ID of a TeamPage object
    :return: a blank HttpResponse on success
    """
    if request.method == 'POST':
        team = TeamPage.objects.get(id=page_id)

        admin = TeamAdministrator.objects.filter(team_page=team)[0]

        entity = RoleController.GetRoleForEntityTypeAndID(
            admin.entity_type,
            admin.entity_id,
            RoleBase.RoleWrapperByEntityType(admin.entity_type)
        )
        email = entity.user.email
        details = team.contact_details
        if details and re.match(r'[\w\.]+\@[\w\.]+\.com$', details):
            email = details

        message = request.POST.get('message', '')
        if message:
            to = ['support@spudder.zendesk.com', email]
            mail.send_mail(
                subject='Message from Spudder about Team: %s' % team.name,
                body=message,
                sender=settings.SERVER_EMAIL,
                to=to
            )
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])