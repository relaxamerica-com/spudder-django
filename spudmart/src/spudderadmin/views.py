import urllib2
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from spudderaccounts.models import SpudderUser
from spudderaccounts.wrappers import RoleStudent
from spudderadmin.decorators import admin_login_required
from spudderadmin.utils import encoded_admin_session_variable_name
from spudderdomain.models import FanPage, LinkedService, TeamAdministrator, TeamPage
from spudderkrowdio.models import KrowdIOStorage
from spuddersocialengine.models import SpudFromSocialMedia, InstagramDataProcessor
from spudmart.CERN.models import Student, School
from spudmart.donations.models import RentVenue
from spudmart.recipients.models import VenueRecipient
from spudmart.sponsors.models import SponsorPage
from spudmart.upload.models import UploadedFile
from spudmart.venues.models import PendingVenueRental, Venue


def admin_login(request):
    error = False
    if request.method == 'POST':
        error = True
        if request.POST.get('username', None) == 'admin@spudder.com' and \
           request.POST.get('password', None) == 'spudmart1':
            request.session[encoded_admin_session_variable_name()] = True
            return redirect(admin_dashboard)
    return render_to_response(
        'spudderadmin/pages/login.html',
        {'error': error},
        context_instance=RequestContext(request))


@admin_login_required
def admin_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/dashboard.html',
        {},
        context_instance=RequestContext(request))


@admin_login_required
def cern_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/cern/dashboard.html',
        {
            'students': [RoleStudent(s) for s in Student.objects.all()]
        },
        context_instance=RequestContext(request))


@admin_login_required
def socialengine_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/socialengine/dashboard.html',
        {
            'spuds': SpudFromSocialMedia.objects.all()[:10]
        },
        context_instance=RequestContext(request))


@admin_login_required
def system_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/system/dashboard.html',
        {},
        context_instance=RequestContext(request))


@admin_login_required
def system_remove_school_cover_images(request):
    if not settings.DEBUG:
        raise Http404
    for school in School.objects.all():
        school.cover_image = None
        school.save()
        UploadedFile.objects.all().delete()
    messages.success(request, 'Schools Reset')
    return redirect('/spudderadmin/system')


@admin_login_required
def system_nukedb(request):
    if not settings.DEBUG:
        raise Http404

    Student.objects.all().delete()
    User.objects.all().delete()
    RentVenue.objects.all().delete()
    SponsorPage.objects.all().delete()
    VenueRecipient.objects.all().delete()
    SpudderUser.objects.all().delete()
    FanPage.objects.all().delete()
    LinkedService.objects.all().delete()
    TeamAdministrator.objects.all().delete()
    TeamPage.objects.all().delete()
    KrowdIOStorage.objects.all().delete()
    PendingVenueRental.objects.all().delete()
    Venue.objects.all().delete()
    # InstagramDataProcessor.objects.all().delete()
    SpudFromSocialMedia.objects.all().delete()
    urllib2.urlopen(settings.SPUDMART_BASE_URL + "/socialengine/api/location_task?key=746fygf472f4o2ri")

    messages.success(request, 'NukeDB Done!!!!')
    return redirect('/spudderadmin/system')
