import settings
from google.appengine.api import mail
import urllib2
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from spudderaccounts.models import SpudderUser
from spudderaccounts.wrappers import RoleStudent, RoleFan, RoleSponsor
from spudderadmin.decorators import admin_login_required
from spudderadmin.utils import encoded_admin_session_variable_name
from spudderdomain.models import FanPage, LinkedService, TeamAdministrator, TeamPage
from spudderkrowdio.models import KrowdIOStorage
from spuddersocialengine.models import SpudFromSocialMedia, InstagramDataProcessor
from spudmart.CERN.models import Student, School
from spudmart.accounts.templatetags.accounts import user_name
from spudmart.donations.models import RentVenue
from spudmart.recipients.models import VenueRecipient
from spudmart.sponsors.models import SponsorPage
from spudmart.upload.models import UploadedFile
from spudmart.venues.models import PendingVenueRental, Venue
from spudmart.CERN.models import Student, STATUS_ACCEPTED, STATUS_REJECTED, \
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
    fans = len(FanPage.objects.all())
    sponsors = len(SponsorPage.objects.all())
    venues = len(Venue.objects.all().exclude(renter=None))
    total_venues = len(Venue.objects.all())
    return render_to_response('spudderadmin/pages/reports/dashboard.html',
        {'fans': fans,
         'sponsors': sponsors,
         'venues': venues,
         'total_venues': total_venues})


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
                              {'sponsorships': sponsorships})
