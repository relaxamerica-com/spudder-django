import os
from urllib2 import urlopen
from datetime import timedelta, datetime
from json import loads

from django.template import RequestContext
from google.appengine.api import mail
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseNotAllowed, HttpResponseForbidden
from spudderdomain.controllers import RoleController
from spudderdomain.models import TeamAdministrator
from spudmart.upload.models import UploadedFile
from spudmart.CERN.models import School, Student, STATES, MailingList
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from spudmart.CERN.utils import import_schools, strip_invalid_chars, add_school_address, convert_referrals
from django.contrib.auth.decorators import user_passes_test
from spudmart.CERN.rep import recruited_new_student, created_venue
from spudmart.utils.cover_image import save_cover_image_from_request, reset_cover_image
from spudmart.utils.queues import trigger_backend_task
from spudmart.utils.url import get_return_url, get_request_param
import settings
from spudmart.venues.models import Venue, SPORTS, TempVenue


def role_is_student(request):
    """
    Determines whether current role is a Student

    Helper method to use with user_passes_test view decorator

    :param request: the full request
    :return: True if role is student and False if not
    """

    return request.current_role.entity_type == RoleController.ENTITY_STUDENT


def user_is_student(user):
    """
    Determines whether user is associated with a student

    Helper method to use with user_passes_test view decorator

    :param user: any user
    :return: True if user is student and False if not
    """
    return user.is_authenticated() and Student.objects.filter(user=user).count()


def user_signin(request):
    return render_to_response(
        'spuddercern/pages/user_signin.html',
        {},
        context_instance=RequestContext(request))


def register(request, referral_id=None):
    """
    Allows users to select a state from a dropdown list, to find school

    :param referral_id: The referral if this is a referral from marketing activity
    :param request: the request to render page
    :return: page where users can select state from a dropwdown list
    """
    if request.method == 'POST':
        return register_with_state(
            request, state=request.POST['state'], referral_id=referral_id)
    sorted_states = sorted(STATES.items(), key=lambda x: x[1])
    template_data = {'states': sorted_states, 'referral_id': referral_id}

    # If we are in dev then print a list of states that have schools in the db. MG: 20140623
    if bool(os.environ['SERVER_SOFTWARE'].startswith('Development')):
        template_data['in_dev_states_with_schools'] = [s.state for s in School.objects.all()]
    return render(
        request, 'spuddercern/pages/register_choose_state.html', template_data)


def register_with_state(request, state, referral_id=None):
    """
    Allows users to select a school (in state) from dropdown list

    :param request: request to render page
    :param state: the standard state abbreviation, capitalized
    :param code: optional param which indicates a referral
    :return: page which allows user to select school from dropwdown
        OR redirect to a school page
    """
    try:
        school_id = request.POST['school']
    except MultiValueDictKeyError:
        schools = []
        for s in School.objects.filter(state=state):
            schools.append(s)
        schools = sorted(schools, key=lambda sch: sch.name)
        return render(request, 'spuddercern/pages/register_choose_school.html',
                      {
                      'state': STATES[state],
                      'abbr': state,
                      'schools': schools,
                      'referral_id': referral_id,
                      })
    else:
        if referral_id:
            return HttpResponseRedirect("/cern/%s/register/%s" %
                                        (school_id, referral_id))
        return HttpResponseRedirect("/cern/%s/register/" % school_id)


def school(request, state, school_id, name, referral_id=None):
    """
    Displays the school splash page

    :param request: request to render page
    :param state: standard state abbreviation of where school is
    :param id: the
    :param name: name of school
        spaces may be replaced by _ in this param
    :param code: optional param which indicates a referral
    :return: rendering of school page or error page if no School with
        name and state combination can be found
    """
    referrer = None

    if referral_id:
        try:
            referrer = Student.objects.get(id=referral_id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/cern/%s/%s/%s/' % (state, school_id, name))

    try:
        sch = School.objects.get(id=school_id)
    except ObjectDoesNotExist:
        return render(request, 'spuddercern/pages/no-school.html')

    stripped_name = strip_invalid_chars(sch.name)
    if strip_invalid_chars(sch.name) != name:
        return HttpResponseRedirect('/cern/%s/%s/%s' % (state, school_id, stripped_name))

    try:
        head = sch.get_head_student()
    except ObjectDoesNotExist:
        head = None

    student = None
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_STUDENT:
        student = request.current_role.entity

    ranked_students = sorted(sch.get_students(), key=lambda s: s.rep(), reverse=True)
    if len(ranked_students) == 0:
        top_students = None
        remaining_students = None
    elif len(ranked_students) <= 5:
        top_students = ranked_students
        remaining_students = None
    else:
        top_students = ranked_students[:5]
        remaining_students = ranked_students[5:]

    if request.method == 'POST':
        sch.description = request.POST.get('description', '')
        sch.mascot = request.POST.get('mascot', '')
        sch.save()

    texts = {}
    if sch.description:
        texts['Description'] = sch.description
    imgs = {}
    if sch.logo:
        imgs['Logo'] = sch.logo.id
    if sch.cover_image:
        imgs['Cover Image'] = sch.cover_image.id

    return render(
        request,
        'spuddercern/pages/school_splash.html', {
            'school': sch,
            'student': student,
            'head': head,
            'user_is_team_member': bool(request.user in ranked_students),
            'referrer': referrer,
            'top_students': top_students,
            'remaining_students': remaining_students,
            'text_fields': texts,
            'img_fields': imgs,
            'base_url': 'spuddercern/base.html',
        })


def save_school_logo(request, school_id):
    """
    Associates a recently-uploaded logo with a school

    :param request: POST request with uploaded image data
    :param school_id: the id of the school
    :return: a blank HttpResponse object if success on POST request
        OR an HttpResponseNotAllowed object (code 405)
    """
    if request.method == 'POST':
        school = School.objects.get(id=school_id)

        request_logo = request.POST.getlist('logo[]')
        logo_id = request_logo[0].split('/')[3]
        logo = UploadedFile.objects.get(pk=logo_id)
        school.logo = logo

        school.save()

        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


def save_school(request, school_id):
    """
    Updates school mascot and description

    :param request: POST request with mascot and description
    :param state: standard state abbreviation for location of school
    :param school_name: name of school
    :return: a blank HttpResponse if success on POST request
        OR an HttpResponseNotAllowed object (code 405)
    """

    if request.method == 'POST':
        school = School.objects.get(id=school_id)

        request_logo = request.POST.getlist('logo[]')
        if len(request_logo):
            logo_id = request_logo[0].split('/')[3]
            logo = UploadedFile.objects.get(pk=logo_id)
            school.logo = logo

        mascot = request.POST['mascot']
        if mascot != '':
            school.mascot = mascot

        description = request.POST['description']
        school.description = description

        school.save()

        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


# @login_required
# @user_passes_test(lambda u: u.is_superuser, '/')
def import_school_data(request):
    trigger_backend_task('/cern/import_schools_async')

    return HttpResponse('Schools are being imported in the background')


def import_school_data_async(request):
    """
    (Re)loads all schools from schools.csv into database

    :param request: request to run import script
    :return: HttpResponseNotAllowed (code 405) if not POST request
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    import_schools()

    return HttpResponse('OK')


def display_cern(request):
    """
    Displays either the CERN dashboard or a splash page about CERN.

    :param request: the request to render page
    :return: the dashboard if a student is logged in OR a splash page
        about CERN
    """
    if request.user.is_authenticated():
        try:
            student = None
            if request.current_role:
                if request.current_role.entity_type == RoleController.ENTITY_STUDENT:
                    student = request.current_role.entity
                else:
                    return redirect('/cern/non-student')
        except ObjectDoesNotExist:
            # In the future, we can create a custom "join spuddercern" page
            #  for existing users
            return cern_splash(request)
        else:
            # check LinkedIn access token
            if student and student.linkedin_token:
                if student.linkedin_expires < datetime.utcnow():
                    urlopen('https://www.linkedin.com/uas/oauth2/authorization' +
                            '?response_type=code' +
                            '&client_id=' + settings.LINKEDIN_API_KEY +
                            '&scope=rw_nus' +
                            '&state=aowj3p5ro8a0f9jq23lk4jqlwkejADSE$SDSDFGJJaw' +
                            '&redirect_uri=http://' + request.META['HTTP_HOST'] +
                            '/cern/save_linkedin')
            return dashboard(request)
    else:
        return cern_splash(request)


def cern_splash(request):
    return render(request, 'spuddercern/pages/splash.html')


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def dashboard(request):
    """
    Displays the CERN dashboard/scoreboard,

    :param request: request to render page
    :return: dashboard customized for logged in student
    """
    student = None
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_STUDENT:
        student = request.current_role.entity

    content = design = qa = True

    try:
        content_list = MailingList.objects.get(project='Blogging')
    except ObjectDoesNotExist:
        pass
    else:
        if student.user.email in content_list.emails:
            content = False

    try:
        design_list = MailingList.objects.get(project='Sponsor Page Design')
    except ObjectDoesNotExist:
        pass
    else:
        if student.user.email in design_list.emails:
            design = False

    try:
        qa_list = MailingList.objects.get(
            project='Quality Assurance Testing')
    except ObjectDoesNotExist:
        pass
    else:
        if student.user.email in qa_list.emails:
            qa = False

    linkedin_key = settings.LINKEDIN_API_KEY

    return render(request, 'spuddercern/pages/dashboard_pages/dashboard.html',
                  {
                  'student': student,
                  'content': content,
                  'design': design,
                  'qa': qa,
                  'key': linkedin_key,
                  })


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def social_media(request):
    """
    Displays social media page with referral links and basic info

    :param request: request to render page
    :return: social media page customized for currently logged in
        student (with custom links and info on top 5 referred users)
    """
    student = request.current_role.entity

    all_referrals = sorted(student.referrals(), key=lambda s: s.rep(),
                       reverse=True)
    num_referred = len(all_referrals)
    if num_referred == 0:
        referrals = None
    else:
        referrals = all_referrals

    need_saving = False

    if student.same_school_referral_url and student.referral_url:
        referral_url = student.referral_url
        same_referral_url = student.same_school_referral_url
    else:
        referral_url = ('http://' + request.META['HTTP_HOST'] +
                        '/cern/register/%s' % student.id)
        same_referral_url = ('http://' + request.META['HTTP_HOST'] +
                             '/cern/%s/register/%s' %
                             (student.school.id,
                             student.id))
        need_saving = True

    return render(request, 'spuddercern/pages/dashboard_pages/social_media.html',
                  {
                  'num_referred': num_referred,
                  'referral_url': referral_url,
                  'same_referral_url': same_referral_url,
                  'student': student,
                  'need_saving': need_saving,
                  'referrals': referrals,
                  })


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def content(request):
    """
    Displays content (blogging) page

    :param request: request to render page
    :return: 'Coming Soon' page customized for content management
    """
    project = 'Blogging'
    joined = False
    try:
        mailing = MailingList.objects.get(project=project)
    except ObjectDoesNotExist:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
    return render(request, 'spuddercern/pages/dashboard_pages/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  'menu_context': 'content'
                  })


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def design(request):
    """
    Displays design page

    :param request: request to render page
    :return: 'Coming Soon' page customized for design
    """
    project = 'Sponsor Page Design'
    joined = False
    try:
        mailing = MailingList.objects.get(project=project)
    except ObjectDoesNotExist:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'spuddercern/pages/dashboard_pages/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  'menu_context': 'design'
                  })


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def testing(request):
    """
    Displays QA testing page

    :param request: request to render page
    :return: qa testing how to in a CERN dashboard page
    """
    # project = 'Quality Assurance Testing'
    # joined = False
    # try:
    #     mailing = MailingList.objects.get(project=project)
    # except ObjectDoesNotExist:
    #     pass
    # else:
    #     if request.user.email in mailing.emails:
    #         joined = True
    #     else:
    #         joined = False
    # return render(request, 'spuddercern/pages/dashboard_pages/coming_soon.html',
    #               {
    #               'project': project,
    #               'joined': joined,
    #               'menu_context': 'testing',
    #               })

    student = None
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_STUDENT:
        student = request.current_role.entity

    return render(request, 'spuddercern/pages/dashboard_pages/qa_testing.html',{
                  'student': student
                  })

# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def mobile(request):
    """
    Displays Mobile page

    :param request: request to render page
    :return: 'Coming Soon' page customized for Mobile
    """
    project = 'Mobile App'
    joined = False
    try:
        mailing = MailingList.objects.get(project=project)
    except ObjectDoesNotExist:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'spuddercern/pages/dashboard_pages/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  'menu_context': 'mobile'
                  })


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def venues(request):
    stu = request.current_role.entity
    template_data = {'venues': Venue.objects.filter(student=stu),
                     'temp_venues': TempVenue.objects.filter(student=stu),
                     'student': stu}
    return render(request, 'spuddercern/pages/dashboard_pages/venues.html', template_data)


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def venues_new(request):
    sorted_states = sorted(STATES.items(), key=lambda x: x[1])
    template_data = {'sports': SPORTS, 'states': sorted_states}
    return render(request, 'spuddercern/pages/venues_new.html', template_data)


# @login_required
@user_passes_test(user_is_student, '/cern/non-student/')
def delete_venue(request, venue_id):
    """
    Deletes a TempVenue
    :param request: a POST request
    :param venue_id: a valid ID of a TempVenue object
    :return: redirect to temp venues list
    """
    venue = TempVenue.objects.get(id=venue_id)
    venue.delete()
    return HttpResponseRedirect('/cern/venues/temp')


def add_email_alert(request):
    """
    Adds an email address to a MailingList for a give project

    :param request: HttpRequest that should include 'project' and
        'email' in POST data
    :return: Blank HttpResponse on success
        OR HttpReponseNotAllowed (code 405) if not POfST request
    """
    if request.method == 'POST':
        project = request.POST['project']

        try:
            mailinglist = MailingList.objects.get(project=project)
        except ObjectDoesNotExist:
            mailinglist = MailingList(emails=[], project=project)

        mailinglist.emails.append(request.POST['email'])
        mailinglist.save()
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


def save_short_url(request):
    """
    Saves goo.gl shortened URL of referral in Student object

    :param request: HttpRequest object that should include
        'referral-url' or 'same-referral-url' in POST data
    :return: Empty HttpResponse object on success
        OR HttpResponseNotAllowed object (code 405) if not POST request
    """
    if request.method == 'POST':
        student = request.current_role.entity
        try:
            referral = request.POST['same-referral-url']
        except MultiValueDictKeyError:
            try:
                referral = request.POST['referral-url']
            except MultiValueDictKeyError:
                pass
            else:
                student.referral_url = referral
        else:
            student.same_school_referral_url = referral
        student.save()
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


def disable_about(request):
    """
    Disables 'about X' part of given page for given student

    :param request: request to disable about, should include 'about'
        param which specifies which 'about' to hide
    :return: a blank HttpResponse on success
    """
    if request.method == 'POST':
        student = request.current_role.entity
        message_id = request.POST.get('message_id')
        if message_id:
            student.dismiss_info_message(message_id)
        return HttpResponse(student.info_messages_dismissed)
    else:
        return HttpResponseNotAllowed(['POST'])


def register_school(request, school_id, referral_id=None):
    """
    Renders the signup page for a new student at a certain school

    :param request: request to render page
    :param school_id: the ID of the school which the student will
        register with
    :param code: an optional param which indicates a referral by
        another student
    :return: a simple login page with the Amazon Login button
    """
    try:
        school = School.objects.get(id=school_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/cern/register/')
    else:
        referrer = None
        if referral_id:
            try:
                referrer = Student.objects.get(id=referral_id)
            except ObjectDoesNotExist:
                pass

        return render(request, 'spuddercern/pages/register_login_with_amazon.html', {
            'school': school,
            'referrer': referrer,
            'base_url': settings.SPUDMART_BASE_URL
        })


def user_not_student_error_page(request):
    """
    Displays an error page when a non-student hits a private CERN page

    :param request: request to render the restricted page
    :return: a simple error page that links to the info page for CERN
    """
    return render(request, 'spuddercern/pages/non-student.html')


def join_school(request, school_id, referral_id=None):
    """
    Makes an existing user into a Student, linked to the given school

    :param request: request to join school
    :param school_id: ID of school
    :return: redirect to school page
    """
    sch = School.objects.get(id=school_id)
    stu = Student(user=request.user, school=sch)

    if sch.num_students() == 0:
        stu.isHead = True

    stu.save()

    # Referral points get added after object saved, so put all referral
    #  stuff in the same place
    if referral_id:
        referrer = Student.objects.get(id=referral_id)
        stu.referred_by = referrer.user
        stu.save()
        recruited_new_student(referrer, sch)

    return HttpResponseRedirect('/cern/')


def login(request):
    return render(request, 'spuddercern/pages/login.html', {
                           'client_id': settings.AMAZON_LOGIN_CLIENT_ID,
                           'base_url': settings.SPUDMART_BASE_URL,
                           'returnURL': get_return_url(request)
    })


def save_linkedin(request):
    """
    Saves linkedin details so that CERN can post to LinkedIn.

    :param request: response from LinkedIn
    :return: redirect to CERN dashboard
    """
    if request.method == 'GET':
        state = 'aowj3p5ro8a0f9jq23lk4jqlwkejADSE$SDSDFGJJaw'
        returned_state = get_request_param(request, 'state')
        if returned_state == state:
            # Handle case when user does not authorize
            if get_request_param(request, 'error') == 'access_denied':
                pass
            code = get_request_param(request, 'code')

            response = urlopen('https://www.linkedin.com/uas/oauth2/accessToken' +
                               '?grant_type=authorization_code' +
                               '&code=' + code +
                               '&redirect_uri=http://' + request.META['HTTP_HOST'] +
                                '/cern/save_linkedin' +
                                '&client_id=' + settings.LINKEDIN_API_KEY +
                                '&client_secret=' + settings.LINKEDIN_SECRET_KEY,
                                data=" ")

            json = loads(response.read())
            seconds_remaining = int(json['expires_in']) - 86400*3
            expires = datetime.utcnow() + timedelta(seconds=seconds_remaining)
            token = json['access_token']

            student = request.current_role.entity
            student.linkedin_token = token
            student.linkedin_expires = expires
            student.save()

            return HttpResponseRedirect('/cern/')
        elif returned_state == '':
            # the request does not come from the LinkedIn API
            return HttpResponseForbidden()
        else:
            # there was a CSRF error, do something else
            pass


def share_marketing_points(request):
    """
    Automatically shares marketing points for current user on LinkedIn

    :param request: a POST request from a user with LinkedIn credentials
    :return: the response from the LinkedIn Share API
    """
    if request.method == 'POST':
        student = request.current_role.entity
        return HttpResponse(student.brag_marketing())
    else:
        return HttpResponseNotAllowed(['POST'])


def share_social_media_points(request):
    """
    Automatically shares social media points for current user on LinkedIn

    :param request: a POST request from a user with LinkedIn credentials
    :return: the response from the LinkedIn Share API
    """
    if request.method == 'POST':
        student = request.current_role.entity
        return HttpResponse(student.brag_social_media())
    else:
        return HttpResponseNotAllowed(['POST'])


def auto_share_marketing(request):
    """
    Toggles whether to auto-share marketing points for current student.

    :param request: request to toggle marketing auto-share
    :return: an HttpResponse with the new state of the auto-sharing
    """
    if request.method == 'POST':
        student = request.current_role.entity
        if student.auto_brag_marketing:
            student.auto_brag_marketing = False
        else:
            student.auto_brag_marketing = True

        student.save()
        return HttpResponse(str(student.auto_brag_marketing))
    else:
        return HttpResponseNotAllowed(['POST'])


def auto_share_social_media(request):
    """
    Toggles whether to auto-share social media points for current student.

    :param request: request to toggle social media auto-share
    :return: an HttpResponse with the new state of auto-sharing
    """
    if request.method == 'POST':
        student = request.current_role.entity
        if student.auto_brag_social_media:
            student.auto_brag_social_media = False
        else:
            student.auto_brag_social_media = True

        student.save()
        return HttpResponse(str(student.auto_brag_social_media))
    else:
        return HttpResponseNotAllowed(['POST'])


def auto_share_marketing_level(request):
    """
    Toggles whether to share Marketing level ups for current student.

    :param request: request to toggle, linked to a user
    :return: an HttpResponse with the new state of level-sharing
    """
    if request.method == 'POST':
        student = request.current_role.entity
        if student.level_brag_marketing:
            student.level_brag_marketing = False
        else:
            student.level_brag_marketing = True

        student.save()
        return HttpResponse(str(student.level_brag_marketing))
    else:
        return HttpResponseNotAllowed(['POST'])


def auto_share_social_media_level(request):
    """
    Toggles whether to share Social Media level ups for current student.

    :param request: request to toggle, linked to a user
    :return: an HttpResponse with the new state of level-sharing
    """
    if request.method == 'POST':
        student = request.current_role.entity
        if student.level_brag_social_media:
            student.level_brag_social_media = False
        else:
            student.level_brag_social_media = True

        student.save()
        return HttpResponse(str(student.level_brag_social_media))
    else:
        return HttpResponseNotAllowed(['POST'])


def save_school_cover(request, school_id):
    """
    Saves a school's new cover image.

    :param request: POST request containing image path (as
        /file/serve/<id>?max_dim=600 )
    :param school_id: ID of the school
    :return: a blank HttpResponse on success
    """
    school = School.objects.get(id=school_id)
    save_cover_image_from_request(school, request)

    return HttpResponse()


def reset_school_cover(request, school_id):
    """
    Resets the school cover image to map by setting field to None
    :param request: POST request
    :param school_id: id of school whose cover is to be reset
    :return: a blank HttpResponse on success
    """
    school = School.objects.get(pk=school_id)
    reset_cover_image(school)

    return HttpResponse()


def student_page(request, student_id):
    """
    Displays the "profile" for the student.

    :param request: request to display the student page
    :param student_id: ID of the student whose information we display
    :return: a page rendered from the student_page template with basic
        details about the student, designed to be consistent with the
        other profile pages on Spudder
    """
    student = Student.objects.get(id=student_id)

    venues = Venue.objects.filter(student=student)

    teams = TeamAdministrator.objects.filter(entity_id=student.id,
                                             entity_type='student').select_related('team_page')

    all_referrals = sorted(student.referrals(), key=lambda s: s.rep(),
                       reverse=True)
    num_referred = len(all_referrals)

    return render(request, 'spuddercern/pages/student_page.html', {
                  'student': student,
                  'venues': venues,
                  'num_referred': num_referred,
                  'top_five': all_referrals[:5],
                  'base_url': 'spuddercern/base.html',
                  'teams': teams
                  })


def save_student_cover(request, student_id):
    """
    Saves a students's new cover image.

    :param request: POST request containing image path (as
        /file/serve/<id>?max_dim=600 )
    :param school_id: ID of the student
    :return: a blank HttpResponse on success
    """
    student = Student.objects.get(id=student_id)
    save_cover_image_from_request(student, request)

    return HttpResponse()


def reset_student_cover(request, student_id):
    """
    Resets the student cover image to map by setting field to None
    :param request: POST request
    :param student_id: id of student whose cover is to be reset
    :return: a blank HttpResponse on success
    """
    student = Student.objects.get(pk=student_id)
    reset_cover_image(student)

    return HttpResponse()


def save_student_logo(request, student_id):
    """
    Associates a recently-uploaded logo with a student

    :param request: POST request with uploaded image data
    :param student_id: the id of the student
    :return: a blank HttpResponse object if success on POST request
        OR an HttpResponseNotAllowed object (code 405)
    """
    if request.method == 'POST':
        student = Student.objects.get(id=student_id)

        request_logo = request.POST.getlist('logo[]')
        if len(request_logo):
            logo_id = request_logo[0].split('/')[3]
            logo = UploadedFile.objects.get(pk=logo_id)
            student.logo = logo

        student.display_name = request.POST['displayName']
        student.append_points = (request.POST['appendPoints'] == 'true')

        student.save()

        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


def save_student_social_media(request, student_id):
    """
    Saves social media links for student

    :param request: POST request containing social media link(s)
    :param student_id: the student whose social media info is updated
    :return: a blank HttpResponse on success
    """
    student = Student.objects.get(id=student_id)

    student.linkedin_link = request.POST['linkedin']
    student.facebook_link = request.POST['facebook']
    student.twitter_link = request.POST['twitter']
    student.google_link = request.POST['google']
    student.instagram_link = request.POST['instagram']

    student.save()
    return HttpResponse()


def upload_student_resume(request, student_id):
    """
    Attaches a resume to a student object so student can apply to QA

    :param request: POST request with resume as string
    :param student_id: ID of student belonging to resume
    :return: a blank HttpResponse on success
    """
    stu = Student.objects.get(id=student_id)

    resume = request.POST['resume']
    stu.resume = resume
    stu.save()

    return HttpResponse()


def apply_qa(request, student_id):
    """
    Marks a student as applied to the QA Testing program.

    :param request: POST request
    :param student_id: id of student with resume who is applying to QA
        program
    :return: a blank HttpResponse on success
    """
    stu = Student.objects.get(id=student_id)

    stu.applied_qa = True
    stu.save()
    return HttpResponse()


def delete_resume(request, student_id):
    """
    Removes a student's resume and application to join QA project.

    :param request: POST request
    :param student_id: id of student losing resume
    :return: a blank HttpResponse on success
    """
    stu = Student.objects.get(id=student_id)
    stu.resume = None
    stu.applied_qa = False
    stu.save()

    return HttpResponse()


def send_help_message(request, student_id):
    """
    Sends a help message to the ZenDesk account from a student.

    :param request: POST request containing message as plain text
    :param student_id: ID of student who sent message
    :return: a blank HttpResponse on success
    """

    stu = Student.objects.get(id=student_id)
    email = stu.user.email

    message = request.POST.get('message', '')
    message += "\n--From Student %s" % email
    project = request.POST.get('project')
    to = ['support@spudder.zendesk.com']
    mail.send_mail(subject='Message from Student about Project %s' % project,
                   body=message, sender=settings.SERVER_EMAIL, to=to)

    return HttpResponse()


def redeem_points(request):
    """
    Displays a page about redeeming CERN points for prizes.
    :param request: any request
    :return: redeem_points page
    """
    return render(request, 'spuddercern/pages/redeem_points.html')


def compensation(request):
    """
    Displays a page about student compensation of venue sponsorship
    :param request: any request
    :return: compensation page
    """
    return render(request, 'spuddercern/pages/compensation.html')


def after_college(request):
    """
    Displays a page about how CERN helps you after college
    :param request: any request
    :return: after_college page
    """
    return render(request, 'spuddercern/pages/after_college.html')


# @login_required
# @user_passes_test(lambda u: u.is_superuser, '/')
def import_school_addrs(request):
    trigger_backend_task('/cern/import_school_addrs_async')

    return HttpResponse('School addresses are being added in the background')


def import_school_addrs_async(request):
    """
    Adds addresses to all existing schools in database

    :param request: request to run import script
    :return: HttpResponseNotAllowed (code 405) if not POST request
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    add_school_address()

    return HttpResponse('OK')


@user_passes_test(user_is_student, '/cern/non-student/')
def edit_school_cover(request, school_id):
    """
    Edit cover template, customized for school
    :param request: any request
    :param school_id: valid ID of a school
    :return: the edit_cover_image template, customized for the school
    """
    sch = School.objects.get(id=school_id)
    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': sch.name,
        'return_url': "/cern/%s/%s/%s" %
                      (sch.state, sch.id, strip_invalid_chars(sch.name)),
        'post_url': '/cern/%s/save_school_cover' % sch.id,
        'reset_url': '/cern/%s/reset_school_cover' % sch.id
    })


@user_passes_test(user_is_student, '/cern/non-student/')
def edit_student_cover(request, student_id):
    """
    Edit cover template, customized for student
    :param request: any request
    :param student_id: valid ID of a student
    :return: the edit_cover_image template, customized for the student
    """
    stu = Student.objects.get(id=student_id)
    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': 'Your Student Page',
        'return_url': "/cern/student/%s" % stu.id,
        'post_url': '/cern/student/%s/save_cover' % stu.id,
        'reset_url': '/cern/student/%s/reset_cover' % stu.id
    })


def translate_referrals(request):
    trigger_backend_task('/cern/translate_referrals_async')

    return HttpResponse('Referrals are being translated in the background')


def translate_referrals_async(request):
    """
    Translates old user-based referrals to new Role-consistent ones

    :param request: request to run import script
    :return: HttpResponseNotAllowed (code 405) if not POST request
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    convert_referrals()

    return HttpResponse('OK')


@user_passes_test(user_is_student, '/cern/non-student/')
def create_temp_venue(request):
    """
    Creates a TempVenue from POST Data, saving location & sport
    :param request: a POST request with location & sport of new venue
    :return: an HttpResponse with ID of new venue on success
    """
    if request.method == 'POST':
        venue = TempVenue(user=request.user, sport=request.POST['sport'], student=request.current_role.entity)
        venue.latitude = float(request.POST['latitude'])
        venue.longitude = float(request.POST['longitude'])
        venue.state = request.POST['state']
        venue.save()

        return HttpResponse("%s" % venue.id)


@user_passes_test(user_is_student, '/cern/non-student/')
def venue_created(request, venue_id):
    """
    Displays a simple well for naming the venue

    Also allows the student to save venue for later, or edit now and
    mark as "live"
    :param request: any request
    :param venue_id: a valid ID of a TempVenue object
    :return: a simple well page with form
    """
    venue = TempVenue.objects.get(id=venue_id)
    return render(request, 'spuddercern/pages/venue_created.html', {
        'venue': venue
    })


@user_passes_test(user_is_student, '/cern/non-student/')
def temp_venue_view(request, venue_id):
    """
    Displays a page like the public venue page, for TempVenues

    Student can edit all info about actual venue, but need to "publish"
        the page before anyone else can see it
    :param request: any request
    :param venue_id: a valid ID of a TempVenue object
    :return: a template like the public venue page, but with limited
        functionality (no sponsorships, no spuds)
    """
    ven = TempVenue.objects.get(id=venue_id)
    if request.current_role.entity == ven.student:
        splitted_address = ven.medical_address.split(', ')
        medical_address = {
            'address': splitted_address.pop(0) if splitted_address else '',
            'city': splitted_address.pop(0) if splitted_address else '',
            'state': splitted_address.pop(0) if splitted_address else '',
            'zip': splitted_address.pop(0) if splitted_address else ''
        }
        return render(request, 'spuddercern/pages/temp_venue.html', {
            'venue': ven,
            'medical_address': medical_address,
            'base_url': 'spuddercern/base.html'
        })
    else:
        return render(request, 'spuddercern/pages/temp_venue_error.html')


@user_passes_test(user_is_student, '/cern/non-student/')
def publish_venue(request, venue_id):
    """
    Converts a TempVenue into a Venue
    :param request: any request
    :param venue_id: a valid ID of a TempVenue object
    :return: a redirect to the supplied next url, or the new venue page
    """
    new_venue = TempVenue.objects.get(id=venue_id).translate_to_real_venue()
    next = request.GET.get('next', '/venues/view/%s' % new_venue.id)
    return HttpResponseRedirect(next)