from django.shortcuts import render
from spudderdomain.models import TeamPage
from spudderdomain.forms import TeamPageForm
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore
from django.http import HttpResponseRedirect, HttpResponse
from spudmart.venues.models import SPORTS
import logging

def teams_list(request):
    teams = TeamPage.objects.filter(admins=request.user)
    return render(request, 'spudderteams/pages/teams.html', { 'teams' : teams })


def team_page(request, page_id=None):
    if page_id:
        page = TeamPage.objects.get(pk = page_id)
    else:
        page = TeamPage()
        page.admins.append(request.user.pk)
    if request.method == 'POST':
        form = TeamPageForm(request.POST, instance=page)
        logging.info(form.errors)
        page_model = form.save(False)
        page_model.team = request.user
        if len(request.FILES) > 0:
            avatar_form = UploadForm(request.POST, request.FILES)
            avatar = avatar_form.save()
            page_model.avatar = avatar
        page_model.save()
        return HttpResponseRedirect('/team/page/%s' % page_model.id)
    form = TeamPageForm(instance=page)
    return render(request, 'spudderteams/pages/team_page_edit.html', 
                  { 'form' : form, 
                   'upload_url' : blobstore.create_upload_url('/team/page/%s' % page.id), 
                   'page' : page,
                   'sports' : SPORTS })


def public_view(request, page_id):
    page = TeamPage.objects.get(pk = page_id)
    return render(request, 'spudderteams/pages/team_page_view.html', { 'page' : page })


def remove_image(request):
    page = TeamPage.objects.get(team = request.user)
    page.image = None
    page.save()
    return HttpResponse('ok')
    