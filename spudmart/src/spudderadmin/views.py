import urllib2

from google.appengine.api import mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

import settings
from spudderaccounts.models import SpudderUser
from spudderaccounts.wrappers import RoleStudent, RoleFan, RoleSponsor
from spudderadmin.decorators import admin_login_required
from spudderadmin.forms import AtPostSpudTwitterAPIForm, SystemDeleteTeamsForm, SystemDeleteVenuesForm
from spudderadmin.utils import encoded_admin_session_variable_name
from spudderdomain.models import FanPage, LinkedService, TeamAdministrator, TeamPage, TeamVenueAssociation
from spudderkrowdio.models import KrowdIOStorage
from spuddersocialengine.atpostspud.models import AtPostSpudTwitterAuthentication, AtPostSpudTwitterCounter, AtPostSpudServiceConfiguration
from spuddersocialengine.models import SpudFromSocialMedia
from spudmart.CERN.models import Student, School, STATES
from spudmart.CERN.templatetags.CERN import student_email
from spudmart.accounts.templatetags.accounts import fan_page_name, user_name
from spudmart.donations.models import RentVenue
from spudmart.recipients.models import VenueRecipient
from spudmart.sponsors.models import SponsorPage
from spudmart.upload.models import UploadedFile
from spudmart.venues.models import PendingVenueRental, Venue
from spudmart.CERN.models import STATUS_ACCEPTED, STATUS_REJECTED, \
    STATUS_WAITLIST


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
            'students': Student.objects.all().count(),
            'schools': Student.objects.filter(isHead=True).count(),

        },
        context_instance=RequestContext(request))


@admin_login_required
def socialengine_dashboard(request):
    template_data = {
        'twitter_auth': AtPostSpudTwitterAuthentication.GetForSite(),
        'at_post_spud_service': AtPostSpudServiceConfiguration.GetForSite()
    }
    return render_to_response(
        'spudderadmin/pages/socialengine/dashboard.html',
        template_data,
        context_instance=RequestContext(request))


@admin_login_required
def socialengine_atpostspud(request):
    template_data = {}
    twitter_auth_model = AtPostSpudTwitterAuthentication.GetForSite()
    at_post_spud_api_form = AtPostSpudTwitterAPIForm(initial=twitter_auth_model.__dict__)
    if request.method == "POST":
        action = request.POST.get('action', None)
        if action == "twitter_api_1":
            at_post_spud_api_form = AtPostSpudTwitterAPIForm(request.POST)
            if at_post_spud_api_form.is_valid():
                for attr in ('api_key', 'api_secret', ):
                    twitter_auth_model.__setattr__(attr, at_post_spud_api_form.cleaned_data.get(attr, ''))
                twitter_auth_model.save()
        if action == "twitter_api_reset":
            twitter_auth_model.reset()
            at_post_spud_api_form = AtPostSpudTwitterAPIForm(initial=twitter_auth_model.__dict__)
        if action == "twitter_api_2":
            pin = request.POST.get('pin', None)
            request_token_key = request.POST.get('request_token_key', None)
            request_token_secret = request.POST.get('request_token_secret', None)
            twitter_auth_model.update_with_pin(pin, request_token_key, request_token_secret)
        if action == "twitter_counter_reset":
            AtPostSpudTwitterCounter.SetLastProcessedId(1)
        if action == 'service_deactivate':
            AtPostSpudServiceConfiguration.GetForSite().deactivate()
        if action == 'service_activate':
            AtPostSpudServiceConfiguration.GetForSite().activate()
        if action == "twitter_test_tweet":
            tweet = request.POST.get('tweet', '')
            twitter_auth_model.api().update_status(tweet)
    template_data['twitter_auth_model'] = twitter_auth_model
    template_data['at_post_spud_api_form'] = at_post_spud_api_form
    auth_url, request_token_key, request_token_secret = twitter_auth_model.get_authorization_url_and_request_token()
    template_data['twitter_auth_url'] = auth_url
    template_data['request_token_key'] = request_token_key
    template_data['request_token_secret'] = request_token_secret
    template_data['twitter_since_id'] = AtPostSpudTwitterCounter.GetLastProcessedId()
    template_data['at_post_spud_service'] = AtPostSpudServiceConfiguration.GetForSite()
    return render_to_response(
        'spudderadmin/pages/socialengine/at_post_spud.html',
        template_data,
        context_instance=RequestContext(request))


@admin_login_required
def system_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/system/dashboard.html',
        {},
        context_instance=RequestContext(request))


@admin_login_required
def system_teams(request):
    template_data = {}
    delete_teams_form = SystemDeleteTeamsForm(initial={'action': "teams_delete"})
    if request.method == "POST":
        action = request.POST['action']
        if action == "teams_delete":
            delete_teams_form = SystemDeleteTeamsForm(request.POST)
            if delete_teams_form.is_valid():
                for team in TeamPage.objects.all():
                    TeamAdministrator.objects.filter(team_page=team).delete()
                    TeamVenueAssociation.objects.filter(team_page=team).delete()
                TeamPage.objects.all().delete()
                messages.success(request, 'Teams deleted')
    template_data['delete_teams_form'] = delete_teams_form
    return render_to_response(
        'spudderadmin/pages/system/teams.html', template_data, context_instance=RequestContext(request))


@admin_login_required
def system_venues(request):
    template_data = {}
    delete_venues_form = SystemDeleteVenuesForm(initial={'action': "venues_delete"})
    if request.method == "POST":
        action = request.POST['action']
        if action == "venues_delete":
            delete_venues_form = SystemDeleteVenuesForm(request.POST)
            if delete_venues_form.is_valid():
                Venue.objects.all().delete()
                messages.success(request, 'Venues deleted')
    template_data['delete_venues_form'] = delete_venues_form
    return render_to_response(
        'spudderadmin/pages/system/venues.html', template_data, context_instance=RequestContext(request))


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



@admin_login_required
def qa_job_board(request):
    """
    Displays the students who have applied to join the QA project

    The admin can mass accept/reject students in this view; they see
        the first 20 words of the student's resume (this is roughly two
        lines of text

    :param request: any request
    :return:
    """
    students = []
    for s in Student.objects.filter(applied_qa=True):
        students.append(s)
    return render_to_response('spudderadmin/pages/cern/qa_job_board.html',
                              {'students': students})


@admin_login_required
def student_resume(request, student_id):
    """
    Displays the full resume for a given student.

    Also allows the admin to accept/reject their QA application
    :param request:
    :param student_id:
    :return:
    """
    stu = Student.objects.get(id=student_id)
    return render_to_response('spudderadmin/pages/cern/resume.html',
                              {'student': stu})


def accept_student(request, student_id):
    """
    Accepts the student into the QA program.

    :param request: a POST request
    :param student_id: a valid student ID
    :return: the updated qa status on success, or HttpResponseNotAllowed
        (code 405) if not a POST request
    """
    if request.method == "POST":
        stu = Student.objects.get(id=student_id)
        stu._qa_status = STATUS_ACCEPTED
        stu.save()
        return HttpResponse(stu._qa_status)
    else:
        return HttpResponseNotAllowed(['POST'])


def reject_student(request, student_id):
    """
    Rejects the student from the QA program.

    :param request: a POST request
    :param student_id: a valid student ID
    :return: the updated qa status on success, or HttpResponseNotAllowed
        (code 405) if not a POST request
    """
    if request.method == "POST":
        stu = Student.objects.get(id=student_id)
        stu._qa_status = STATUS_REJECTED
        stu.save()
        return HttpResponse(stu._qa_status)
    else:
        return HttpResponseNotAllowed(['POST'])


def waitlist_student(request, student_id):
    """
    Put the student on the QA waitlist.

    :param request: a POST request
    :param student_id: a valid student ID
    :return: the updated qa status on success, or HttpResponseNotAllowed
        (code 405) if not a POST request
    """
    if request.method == "POST":
        stu = Student.objects.get(id=student_id)
        stu._qa_status = STATUS_WAITLIST
        stu.save()
        return HttpResponse(stu._qa_status)
    else:
        return HttpResponseNotAllowed(['POST'])


def send_email(request):
    """
    Sends message to email (supplied in request)
    :param request: a POST request containing message body and subject,
        plus address toe mail to
    :return: a blank HttpResponse on success, or HttpResponseNotAllowed
        (ode 405) if not a POST request
    """
    if request.method == "POST":
        body = request.POST.get('body', '')
        to = [request.POST.get('to', '')]
        subject = request.POST.get('subject', '')
        sender = settings.SUPPORT_EMAIL

        mail.send_mail(subject=subject, body=body, sender=sender, to=to)
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


@admin_login_required
def send_student_email(request, student_id):
    """
    Allows admin to compose an email to the student
    :param request: any request
    :param student_id: a valid Student ID
    :return: send_student_email template customized for this student
    """
    stu = Student.objects.get(id=student_id)
    return render_to_response('spudderadmin/pages/cern/send_student_email.html',
        {'student': stu})


@admin_login_required
def fan_reports(request):
    """
    Displays a general report on all fans (with search)
    :param request: any request
    :return: a table of all fans with some basic info, plus functional
        search box
    """
    fans = FanPage.objects.all()
    return render_to_response('spudderadmin/pages/reports/fans.html',
        {'fans': [RoleFan(fan) for fan in fans]})


@admin_login_required
def send_fan_email(request, fan_id):
    """
    Allows admin to compose an email to the fan
    :param request: any request
    :param fan_id: a valid FanPage ID
    :return: simple page to compose email to fan
    """
    fan = FanPage.objects.get(id=fan_id)
    email = RoleFan(fan).user.email
    name = fan.name or email
    return render_to_response(
        'spudderadmin/pages/reports/send_email.html',
        {
            'name': name,
            'email': email,
            'profile': '/fan/%s' % fan.id
        })


@admin_login_required
def user_reports_dashboard(request):
    """
    A simple splash page for user reports
    :param request: any request
    :return: a very minimal admin page inside the User Reports
    """
    return render_to_response('spudderadmin/pages/reports/dashboard.html',
        {'fans': FanPage.objects.all().count(),
         'sponsors': SponsorPage.objects.all().count(),
         'venues': Venue.objects.all().exclude(renter=None).count(),
         'total_venues': Venue.objects.all().count(),
         'teams': TeamPage.objects.all().count()})


@admin_login_required
def sponsor_reports(request):
    """
    A table of all sponsors with some basic info
    :param request: any request
    :return: a simple table with basic info about sponsors and links to
        more detailed sponsor pages
    """
    sponsors = [RoleSponsor(s) for s in SponsorPage.objects.all()]
    return render_to_response('spudderadmin/pages/reports/sponsors.html',
        {'sponsors': sponsors})


@admin_login_required
def send_sponsor_email(request, sponsor_id):
    """
    Allows admin to compose an email to the sponsor
    :param request: any request
    :param sponsor_id: a valid SponsorPage ID
    :return: simple page to compose email to sponsor
    """
    sponsor = SponsorPage.objects.get(id=sponsor_id)
    if sponsor.email:
        email = sponsor.email
    else:
        email = RoleSponsor(sponsor).user.email
    return render_to_response('spudderadmin/pages/reports/send_email.html',
        {'name': sponsor.name,
         'email': email,
         'profile': '/sponsor/%s' % sponsor.id
        })


@admin_login_required
def sponsorships(request, sponsor_id):
    """
    Provides details on a sponsor's sponsorships
    :param request: any request
    :param sponsor_id: the valid ID of a SponsorPage object
    :return: a table of information about the venues sponsored by the
        given sponsor, and the actual transactions
    """
    sponsor = SponsorPage.objects.get(id=sponsor_id)
    venues = Venue.objects.filter(renter=sponsor)
    sponsorships = [(v, RentVenue.objects.get(venue=v)) for v in venues]

    return render_to_response('spudderadmin/pages/reports/sponsorships.html',
        {'name': sponsor.name,
         'sponsorships': sponsorships})


@admin_login_required
def all_sponsorships(request):
    """
    Provides details on all Spudder sponsorships
    :param request: any request
    :return: a table of information about sponsored venues, including
        transaction details and venue's sponsor
    """
    venues = Venue.objects.all().exclude(renter=None)
    sponsorships = [(v, RentVenue.objects.get(venue=v)) for v in venues]

    return render_to_response('spudderadmin/pages/reports/all_sponsorships.html',
                              {'sponsorships': sponsorships},
                              context_instance=RequestContext(request))


@admin_login_required
def schools(request):
    """
    Overview of all active schools
    :param request: any request
    :return: a table of all schools
    """
    return render_to_response('spudderadmin/pages/cern/schools.html',
           {
               'students': Student.objects.filter(isHead=True).select_related('school')
           },
           context_instance=RequestContext(request))


@admin_login_required
def students(request):
    """
    Overview of all active students
    :param request: any request
    :return: a table of all students
    """
    return render_to_response('spudderadmin/pages/cern/students.html',
           {
               'students': Student.objects.all()
           },
           context_instance=RequestContext(request))


    @admin_login_required
    def teams(request):
        """
        Overview of Spudder Teams
        :param request: any request
        :return: a table of all Teams with Team Administrator
        """
        return render_to_response('spudderadmin/pages/reports/teams.html',
                                  {
                                      'teams': TeamAdministrator.objects.all().select_related('team_page')
                                  },
                                  context_instance=RequestContext(request))


    @admin_login_required
    def send_team_admin_email(request, admin_id):
        """
        Renders simple page for emailing the a Team admin
        :param request: any request
        :param admin_id: a valid id of a TeamAdministrator object
        :return: a very simple form
        """
        admin = TeamAdministrator.objects.get(id=admin_id)
        profile = name = email = ""

        if admin.entity_type == 'fan':
            profile = "/fan/%s" % admin.entity_id
            fan = FanPage.objects.get(id=admin.entity_id)
            name = fan_page_name(fan)
            email = fan.fan.email
        elif admin.entity_type == 'student':
            profile = "/cern/student/%s" % admin.entity_id
            stu = Student.objects.get(id=admin.entity_id)
            name = user_name(stu.user) or stu.display_name or 'No Name'
            email = student_email(stu)

        return render_to_response('spudderadmin/pages/reports/send_email.html',
                                  {
                                      'profile': profile,
                                      'name': name,
                                      'email': email
                                  },
                                  context_instance=RequestContext(request))