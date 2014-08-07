from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from spudderdomain.models import FanPage
from spudderdomain.forms import FanPageForm
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from spudmart.upload.models import UploadedFile


@login_required
def fan_page(request):
    page = FanPage.objects.get(fan=request.user)
    form = FanPageForm(instance=page)
    should_show_quote = not page.was_edited()

    if request.method == 'POST':
        form = FanPageForm(request.POST, instance=page)
        updated_page = form.save(False)
        updated_page.fan = request.user
        updated_page.save()

        next_url = request.POST.get('next_url', None)
        if not next_url:
            next_url = '/fan/page'

        return HttpResponseRedirect(next_url)

    return render(request, 'spudderfans/pages/fan_page_edit.html', {
        'form': form,
        'page': page,
        'should_show_quote': should_show_quote
    })


def view(request, page_id):
    if page_id:
        page = get_object_or_404(FanPage, pk=page_id)
    else:
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/')

        try:
            page = FanPage.objects.get(fan=request.user)
        except FanPage.DoesNotExist:
            return HttpResponseRedirect('/')

    return render(request, 'spudderfans/pages/fan_page_view.html', {
        'page': page,
        'can_edit': request.user.id == page.fan.id
    })


def fan_dashboard(request):
    return render(request, 'spudderfans/pages/dashboard.html')


def remove_avatar(request):
    page = FanPage.objects.get(fan = request.user)
    page.avatar = None
    page.save()
    return HttpResponse('ok')


def save_avatar(request, page_id):
    avatar_id = request.POST['avatar'].split('/')[3]
    avatar = get_object_or_404(UploadedFile, pk=avatar_id)

    page = get_object_or_404(FanPage, pk=page_id)
    page.avatar = avatar
    page.save()

    return HttpResponse('ok')

def save_cover(request):
    pass

def reset_cover(request):
    pass