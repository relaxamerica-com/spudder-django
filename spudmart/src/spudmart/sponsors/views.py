from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render
import settings
from spudmart.files.forms import UploadForm
from spudmart.sponsors.forms import SponsorPageForm
from spudmart.sponsors.models import SponsorPage
from google.appengine.ext import blobstore


def _get_map_info(post_data):
    return post_data.get('infoLat', '') + ';' + post_data.get('infoLng', '') + ';' + post_data.get('infoWindow', '')


@login_required
@user_passes_test(lambda user: user.is_sponsor)
def sponsor_page(request):
    sponsor_page_instances = SponsorPage.objects.filter(sponsor=request.user)
    lat = None
    lng = None
    info_window = None
    page = None
    upload_form = UploadForm()
    upload_url = blobstore.create_upload_url('/dashboard/sponsor/page')

    if len(sponsor_page_instances):
        page = sponsor_page_instances[0]
        form = SponsorPageForm(instance=page)
        if page.map_info:
            lat, lng, info_window = page.map_info.split(';')
    else:
        form = SponsorPageForm()

    if page and not page.images:
        page.images = ['', '', '']

    if request.method == "POST":
        form = SponsorPageForm(request.POST, instance=page)

        if form.is_valid():
            saved_page = form.save(commit=False)
            saved_page.sponsor = request.user
            saved_page.map_info = _get_map_info(request.POST)

            if len(request.FILES) > 0:
                up_form = UploadForm(request.POST, request.FILES)
                uploaded_file = up_form.save(False)
                uploaded_file.owner = request.user
                uploaded_file.content_type = request.FILES['file'].content_type
                uploaded_file.filename = request.FILES['file'].name
                uploaded_file.save()

                saved_page.thumbnail = uploaded_file

            saved_page.save()

            return HttpResponseRedirect('/dashboard/sponsor/page')

    return render(request, 'dashboard/sponsors/sponsor_page.html', {
        'form': form,
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'lat': lat, 'lng': lng, 'info_window': info_window,
        'page': page,
        'upload_url': upload_url,
        'upload_form': upload_form,
        'images_range': range(3)
    })


@login_required
@user_passes_test(lambda user: user.is_sponsor)
def remove_image(request, image_id):
    page = SponsorPage.objects.get(sponsor=request.user)
    page.images.remove(image_id)
    page.images.append('')
    page.save()

    return HttpResponseRedirect('/dashboard/sponsor/page')


@login_required
@user_passes_test(lambda user: user.is_sponsor)
def add_image(request):
    page = SponsorPage.objects.get(sponsor=request.user)
    upload_form = UploadForm()
    upload_url = blobstore.create_upload_url('/dashboard/sponsor/page/add_image')

    if request.method == "POST":
        if len(request.FILES) > 0:
            up_form = UploadForm(request.POST, request.FILES)
            uploaded_file = up_form.save(False)
            uploaded_file.owner = request.user
            uploaded_file.content_type = request.FILES['file'].content_type
            uploaded_file.filename = request.FILES['file'].name
            uploaded_file.save()

            if page.images:
                index = page.images.index('')
                page.images[index] = uploaded_file.id
            else:
                page.images = [uploaded_file.id, '', '']
            page.save()

        return HttpResponseRedirect('/dashboard/sponsor/page')

    return render(request, 'dashboard/sponsors/add_image.html', {
        'upload_url': upload_url,
        'upload_form': upload_form
    })