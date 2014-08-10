from django.shortcuts import render, redirect, get_object_or_404
import settings
from spudderdomain.controllers import TeamsController
from spudderdomain.models import TeamPage, Location, TeamAdministrator, TeamVenueAssociation
from spudmart.teams.forms import CreateTeamForm, TeamPageForm
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore
from django.http import HttpResponseRedirect, HttpResponse
from spudmart.upload.models import UploadedFile
from spudmart.utils.Paginator import EntitiesPaginator
from spudmart.utils.cover_image import save_cover_image_from_request, reset_cover_image
from spudmart.venues.models import SPORTS, Venue


def teams_list(request):
    teams = TeamsController.TeamsAdministeredByRole(request.current_role)
    return render(request, 'spudderteams/pages/dashboard_pages/teams.html', {'teams': teams})


def create_team(request):
    form = CreateTeamForm
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            image_form = UploadForm(request.POST, request.FILES)
            image = None
            if image_form.is_valid():
                image = image_form.save()

            TeamsController.CreateTeam(
                request.current_role,
                name=form.cleaned_data.get('team_name'),
                contact_details=form.cleaned_data.get('contact_details'),
                free_text=form.cleaned_data.get('free_text'),
                sport=dict(form.fields['sport'].choices)[form.cleaned_data.get('sport')],
                image=image)

            return redirect('/team/list')
    return render(request, 'spudderspuds/teams/pages/create_team.html', {
        'form': form,
        'upload_url': blobstore.create_upload_url('/team/create'),
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

    return render(request, 'spudderteams/pages/dashboard_pages/team_page_edit.html', {
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'page': page,
        'form': form,
        'sports': SPORTS
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
    is_associated, associated_venue = _check_if_team_is_associated(page)

    return render(request, 'spudderteams/pages/team_page_view.html',{
        'page': page,
        'can_edit': can_edit(request.user, request.current_role, page),
        'is_associated': is_associated,
        'venue': associated_venue,
    })


def save_avatar(request, page_id):
    avatar_id = request.POST['avatar'].split('/')[3]
    avatar = get_object_or_404(UploadedFile, pk=avatar_id)

    page = get_object_or_404(TeamPage, pk=page_id)
    page.image = avatar
    page.save()

    return HttpResponse('ok')


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


def _check_if_team_is_associated(page):
    is_associated = TeamVenueAssociation.objects.filter(team_page=page).count() > 0

    if is_associated:
        associated_venue = TeamVenueAssociation.objects.get(team_page=page).venue
    else:
        associated_venue = None

    return is_associated, associated_venue


def associate_with_venue(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    venues = Venue.objects.all().order_by('name')
    is_associated, associated_venue = _check_if_team_is_associated(page)

    # Pagination
    current_page = int(request.GET.get('page',1))
    venues_paginator = EntitiesPaginator(venues, 20)
    venue_page = venues_paginator.page(current_page)

    return render(request, 'spudderteams/pages/dashboard_pages/associate_with_venue.html', {
        'page': page,
        'is_associated': is_associated,
        'associated_venue': associated_venue,
        'venues': venue_page.object_list,
        'total_pages': venues_paginator.num_pages,
        'paginator_page': venue_page.number,
        'start': venue_page.start_index(),
    })


def remove_association_with_venue(request, page_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    TeamVenueAssociation.objects.get(team_page=page).delete()

    return HttpResponseRedirect('/team/associate/%s' % page_id)


def associate_team_with_venue(request, page_id, venue_id):
    page = get_object_or_404(TeamPage, pk=page_id)
    venue = get_object_or_404(Venue, pk=venue_id)

    TeamVenueAssociation(
        team_page=page,
        venue=venue
    ).save()

    return HttpResponseRedirect('/team/list')