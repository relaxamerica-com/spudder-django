from django.shortcuts import render, get_object_or_404
from spudderdomain.models import FanPage
from spudderdomain.forms import FanPageForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from spudmart.upload.models import UploadedFile
from spudmart.utils.cover_image import save_cover_image_from_request, reset_cover_image


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


def save_avatar(request, page_id):
    avatar_id = request.POST['avatar'].split('/')[3]
    avatar = get_object_or_404(UploadedFile, pk=avatar_id)

    page = get_object_or_404(FanPage, pk=page_id)
    page.avatar = avatar
    page.save()

    return HttpResponse('ok')


def edit_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': 'Fan Page',
        'return_url': "/fan/%s" % page.id,
        'post_url': '/fan/%s/save_cover' % page.id,
        'reset_url': '/fan/%s/reset_cover' % page.id
    })


def save_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    save_cover_image_from_request(page, request)

    return HttpResponse()


def reset_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    reset_cover_image(page)

    return HttpResponse('OK')