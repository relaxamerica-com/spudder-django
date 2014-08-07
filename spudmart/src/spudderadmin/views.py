import urllib2
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotAllowed
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
    :return: a blank HttpResponse on success, a HttpResponseNotAllowed
        (code 403) if not a POST request
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
    :return: a blank HttpResponse on success, a HttpResponseNotAllowed
        (code 403) if not a POST request
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
    :return: a blank HttpResponse on success, a HttpResponseNotAllowed
        (code 403) if not a POST request
    """
    if request.method == "POST":
        stu = Student.objects.get(id=student_id)
        stu._qa_status = STATUS_WAITLIST
        stu.save()
        return HttpResponse(stu._qa_status)
    else:
        return HttpResponseNotAllowed(['POST'])