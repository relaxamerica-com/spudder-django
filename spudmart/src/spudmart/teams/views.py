from django.shortcuts import render, redirect, get_object_or_404
import settings
from spudderdomain.controllers import TeamsController, RoleController
from spudderdomain.models import TeamPage, Location, TeamAdministrator, TeamVenueAssociation
from spudmart.teams.forms import CreateTeamForm, TeamPageForm
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore
from django.http import HttpResponseRedirect, HttpResponse
from spudmart.upload.models import UploadedFile
from spudmart.utils.Paginator import EntitiesPaginator
from spudmart.utils.cover_image import save_cover_image_from_request, reset_cover_image
from spudmart.CERN.models import STATES
from spudmart.venues.models import SPORTS, Venue


def teams_list(request):
    teams = TeamsController.TeamsAdministeredByRole(request.current_role)

    role_dashboard = ''
    if request.current_role.entity_type == RoleController.ENTITY_STUDENT:
        role_dashboard = 'spuddercern/pages/dashboard_pages/dashboard.html'
    elif request.current_role.entity_type == RoleController.ENTITY_FAN:
        role_dashboard = 'spudderfans/pages/dashboard.html'
    return render(request, 'components/sharedpages/teams/teams_list.html',
                  {'teams': teams,
                   'role_dashboard': role_dashboard})


def create_team(request):
    form = CreateTeamForm(initial={'next_url': request.GET.get('next_url')})
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            team = TeamsController.CreateTeam(
                request.current_role,
                name=form.cleaned_data.get('team_name'),
                contact_details=form.cleaned_data.get('contact_details'),
                free_text=form.cleaned_data.get('free_text'),
                sport=dict(form.fields['sport'].choices)[form.cleaned_data.get('sport')],
                state=dict(form.fields['state'].choices)[form.cleaned_data.get('state')],
            )
            location_info = request.POST.get('location_info', None)
            team.update_location(location_info)
            team.save()
            return redirect(request.POST.get('next_url', '/team/list'))
    return render(request, 'spudderspuds/teams/pages/create_team.html', {
        'form': form,
        # 'upload_url': blobstore.create_upload_url('/team/create'),
        'SPORTS': SPORTS
    })


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

    if request.method == 'POST':
        form = TeamPageForm(request.POST, instance=page)

        if form.is_valid():
            updated_page = form.save(commit=False)

            location_info = request.POST['location_info']
            updated_page.update_location(location_info)

            updated_page.save()

            return HttpResponseRedirect('/team/page/%s' % page_id)

    form = TeamPageForm(instance=page)

    return render(request, 'spudderspuds/teams/pages/dashboard_pages/team_page_edit.html', {
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'page': page,
        'form': form,
        'sports': SPORTS,
        # 'selected_state' : STATES[page.state],
        # 'states' : STATES
    })


def public_view(request, page_id):
    def can_edit(user, current_role, page):
        if not user.is_authenticated():
            return False

        if not current_role:
            return False

        entity_id = current_role.entity.id
        entity_type = current_role.entity_type
        admins = TeamAdministrator.objects.filter(team_page=page, entity_type=entity_type, entity_id=entity_id)

        return len(admins) > 0

    page = get_object_or_404(TeamPage, pk=page_id)
    is_associated, associated_venues = _check_if_team_is_associated(page)

    return render(request, 'spudderspuds/teams/pages/team_page_view.html',{
        'page': page,
        'can_edit': can_edit(request.user, request.current_role, page),
        'is_associated': is_associated,
        'venues': associated_venues,
    })


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
       'teams' : teams,
       'sports' : SPORTS,
       'states' : STATES,
       'filters' : filters
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
    venues_objects = Venue.objects.all().order_by('name')
    is_associated, associated_venues = _check_if_team_is_associated(page)
    venues = []

    for venue in venues_objects:
        if venue not in associated_venues:
            venues.append(venue)


    # Pagination
    current_page = int(request.GET.get('page',1))
    venues_paginator = EntitiesPaginator(venues, 20)
    venue_page = venues_paginator.page(current_page)

    role_dashboard = ''
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

    return HttpResponseRedirect('/team/%s' % page_id)


def associate_team_with_venue(request, page_id, venue_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    venue = get_object_or_404(Venue, pk=venue_id)
    TeamVenueAssociation(team_page=page, venue=venue).save()
    return HttpResponseRedirect('/team/%s' % page_id)
