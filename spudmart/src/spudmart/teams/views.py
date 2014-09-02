from django.shortcuts import render, redirect, get_object_or_404
from google.appengine.api import blobstore
import settings
from spudderaccounts.templatetags.spudderaccountstags import is_fan, is_cern_student
from spudderdomain.controllers import TeamsController, RoleController, SpudsController, SocialController
from spudderdomain.models import TeamPage, Location, TeamVenueAssociation, TeamAdministrator
from spudderspuds.forms import LinkedInSocialMediaForm
from spudderspuds.utils import set_social_media
from spudmart.CERN.rep import created_team, team_associated_with_venue
from spudmart.teams.forms import CreateTeamForm, TeamPageForm, EditTeamForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
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