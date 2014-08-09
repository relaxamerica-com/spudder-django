from django.shortcuts import render, redirect
import settings
from spudderdomain.controllers import TeamsController
from spudderdomain.models import TeamPage, Location
# from spudderdomain.forms import TeamPageForm
from spudmart.teams.forms import CreateTeamForm, TeamPageForm
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore
from django.http import HttpResponseRedirect, HttpResponse
from spudmart.venues.models import SPORTS
import logging


def teams_list(request):
    teams = TeamsController.TeamsAdministeredByRole(request.current_role)
    return render(request, 'spudderteams/pages/teams.html', {'teams': teams})


def create_team(request):
    form = CreateTeamForm
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            image_form = UploadForm(request.POST, request.FILES)
            image = None
            if image_form.is_valid():
                image = image_form.save()

            team = TeamsController.CreateTeam(
                request.current_role,
                name=form.cleaned_data.get('team_name'),
                contact_details=form.cleaned_data.get('contact_details'),
                free_text=form.cleaned_data.get('free_text'),
                sport=dict(form.fields['sport'].choices)[form.cleaned_data.get('sport')],
                image=image)
            return redirect('/team/page/%s' % team.id)
    return render(
        request, 'spudderspuds/teams/pages/create_team.html',
        {'form': form, 'upload_url': blobstore.create_upload_url('/team/create')})


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

    return render(request, 'spudderteams/pages/team_page_edit.html', {
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'page': page,
        'form': form,
        'sports': SPORTS
    })


def public_view(request, page_id):
    page = TeamPage.objects.get(pk = page_id)
    return render(request, 'spudderteams/pages/team_page_view.html', { 'page' : page })


def remove_image(request):
    page = TeamPage.objects.get(team = request.user)
    page.image = None
    page.save()
    return HttpResponse('ok')
    