from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404
import settings
from spudmart.sponsors.forms import SponsorPageForm
from spudmart.sponsors.models import SponsorPage
from spudmart.accounts.utils import is_sponsor
from spudmart.venues.models import Venue


def _get_map_info(post_data):
    return post_data.get('infoLat', '') + ';' + post_data.get('infoLng', '') + ';' + post_data.get('infoWindow', '')


def _get_thumbnail_id(post_data):
    thumbnail_url = post_data.get('image4', '')
    return thumbnail_url.split('/file/serve/')[1] if thumbnail_url else ''


def _get_image_id(post_data, index):
    url = post_data.get('image%s' % index, '')

    return url.split('/file/serve/')[1] if url else ''


def _get_images_from_post(post_data):
    images = []
    for i in range(1,4):
        image = _get_image_id(post_data, i)
        if image:
            images.append(image)
    for i in range(len(images), 3):
        images.append('')

    return images


@login_required
@user_passes_test(lambda user: is_sponsor(user))
def sponsor_page(request):
    sponsor_page_instances = SponsorPage.objects.filter(sponsor=request.user)
    lat = None
    lng = None
    info_window = None
    page = None

    if len(sponsor_page_instances):
        page = sponsor_page_instances[0]
        form = SponsorPageForm(instance=page)
        if page.map_info:
            lat, lng, info_window = page.map_info.split(';')
    else:
        form = SponsorPageForm()

    if page:
        page.images = filter(lambda image: image != "", page.images)

    if request.method == "POST":
        form = SponsorPageForm(request.POST, instance=page)

        if form.is_valid():
            saved_page = form.save(commit=False)
            saved_page.sponsor = request.user
            saved_page.map_info = _get_map_info(request.POST)
            saved_page.images = _get_images_from_post(request.POST)
            saved_page.thumbnail = _get_thumbnail_id(request.POST)
            saved_page.save()

            return HttpResponseRedirect('/dashboard/sponsor/page')

    return render(request, 'spuddercern/sponsor_dashboard/sponsor_page.html', {
        'form': form,
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'lat': lat, 'lng': lng, 'info_window': info_window,
        'page': page,
        'images_range': range(3)
    })


def public_view(request, page_id):
    page = get_object_or_404(SponsorPage, pk=page_id)
    page.images = filter(lambda image: image != "", page.images)

    return render(request, 'old/sponsors/public_view.html', {
        'page': page
    })


def sponsors_dashboard(request):
    return render(request, 'spuddersponsors/pages/dashboard_pages/dashboard.html')


def sponsors_venues(request):
    sponsor = request.current_role.entity
    venues = Venue.objects.filter(renter=sponsor)

    return render(request, 'spuddersponsors/pages/dashboard_pages/venues.html', {
        'venues': venues
    })