from django.shortcuts import render
from spudderdomain.models import FanPage
from spudderdomain.forms import FanPageForm
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore
from django.http import HttpResponseRedirect, HttpResponse


def fan_page(request):
    page = FanPage.objects.get(fan = request.user)
    if request.method == 'POST':
        form = FanPageForm(request.POST, instance=page)
        page_model = form.save(False)
        page_model.fan = request.user
        if len(request.FILES) > 0:
            avatar_form = UploadForm(request.POST, request.FILES)
            avatar = avatar_form.save()
            page_model.avatar = avatar
        page_model.save()
        return HttpResponseRedirect('/fan/page')
    form = FanPageForm(instance=page)
    return render(request, 'spudderfans/pages/fan_page_edit.html', 
                  { 'form' : form, 
                   'upload_url' : blobstore.create_upload_url('/fan/page'), 
                   'page' : page })


def public_view(request, page_id):
    page = FanPage.objects.get(pk = page_id)
    return render(request, 'spudderfans/pages/fan_page_view.html', { 'page' : page })


def fan_dashboard(request):
    return render(request, 'spudderfans/pages/dashboard.html')


def remove_avatar(request):
    page = FanPage.objects.get(fan = request.user)
    page.avatar = None
    page.save()
    return HttpResponse('ok')
    
def save_avatar(request):
    pass

def save_social_media(request):
    pass

def save_cover(request):
    pass

def reset_cover(request):
    pass