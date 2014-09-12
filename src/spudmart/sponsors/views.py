from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
import settings
from spudmart.sponsors.decorators import current_role_is_sponsor
from spudmart.sponsors.forms import SponsorPageForm
from spudmart.sponsors.models import SponsorPage
from spudmart.venues.models import Venue
from spudmart.utils.cover_image import reset_cover_image, save_cover_image_from_request


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


def user_signin(request):
    return render(request, 'spuddersponsors/pages/register_signin.html')


def user_register(request):
    return render(request, 'spuddersponsors/pages/register_signin.html', {'register': True})


def sponsors_splash(request):
    return render(request, 'spuddersponsors/pages/splash.html')


def public_view(request, page_id):
    page = get_object_or_404(SponsorPage, pk=page_id)
    page.images = filter(lambda image: image != "", page.images)
    longitude = None
    latitude = None

    if page.map_info:
        longitude, latitude, _ = page.map_info.split(';')

    venues = Venue.objects.filter(renter=page)

    return render(request, 'spuddersponsors/pages/dashboard_pages/sponsor_page_view.html', {
        'page': page,
        'latitude': latitude,
        'longitude': longitude,
        'venues': venues,
        'base_url': 'spuddercern/base.html'
    })


@current_role_is_sponsor
def sponsor_page(request):
    page = SponsorPage.objects.get(pk=request.current_role.entity.id)
    lat = None
    lng = None
    info_window = None

    form = SponsorPageForm(instance=page)
    if page.map_info:
        lat, lng, info_window = page.map_info.split(';')

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

            return HttpResponseRedirect('/sponsor/page')

    return render(request, 'spuddersponsors/pages/dashboard_pages/sponsor_page_edit.html', {
        'form': form,
        'places_api_key': settings.GOOGLE_PLACES_API_KEY,
        'lat': lat, 'lng': lng, 'info_window': info_window,
        'page': page,
        'images_range': range(3)
    })


def edit_cover(request, page_id):
    page = SponsorPage.objects.get(id=page_id)

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': page.name,
        'return_url': "/sponsor/%s" % page.id,
        'post_url': '/sponsor/save_cover/%s' % page.id,
        'reset_url': '/sponsor/reset_cover/%s' % page.id
    })


def save_cover(request, page_id):
    page = SponsorPage.objects.get(id=page_id)
    save_cover_image_from_request(page, request)

    return HttpResponse()


def reset_cover(request, page_id):
    page = SponsorPage.objects.get(pk=page_id)
    reset_cover_image(page)

    return HttpResponse('OK')


def save_logo_and_name(request, page_id):
    page = SponsorPage.objects.get(pk=page_id)

    request_logo = request.POST.getlist('logo[]')
    if len(request_logo):
        thumbnail_id = request_logo[0].split('/')[3]
        page.thumbnail = thumbnail_id

    page.name = request.POST['name']
    page.tag = request.POST['tag']
    page.save()

    return HttpResponse('OK')


@current_role_is_sponsor
def sponsors_dashboard(request):
    return render(request, 'spuddersponsors/pages/dashboard_pages/dashboard.html')


@current_role_is_sponsor
def sponsors_venues(request):
    sponsor = request.current_role.entity
    venues = Venue.objects.filter(renter=sponsor)
    return render(request, 'spuddersponsors/pages/dashboard_pages/venues.html', {'venues': venues})