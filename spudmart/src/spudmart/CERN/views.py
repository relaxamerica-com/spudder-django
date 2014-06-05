from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseNotAllowed
from spudmart.upload.models import UploadedFile
from spudmart.CERN.models import School, Student, STATES, MailingList
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from spudmart.CERN.utils import import_schools
from django.contrib.auth.decorators import login_required
from spudmart.utils.url import get_return_url, get_request_param
import urllib
import urllib2
import settings
import json
from django.contrib.auth import authenticate, login
from spudmart.accounts.models import UserProfile
from spudmart.accounts.views import _handle_amazon_conn_error
from spudmart.CERN.rep import recruited_new_student


def register(request, code=None):
    """
    Allows users to select a state from a dropdown list, to find school

    :param request: the request to render page
    :param code: optional param which indicates a referral
    :return: page where users can select state from a dropwdown list
    """
    sorted_states = sorted(STATES.items(), key=lambda x: x[1])
    
    if request.method == 'POST':
        return register_with_state(request, state=request.POST['state'],
                                   code=code)

    return render(request, 'CERN/register.html',
                  {
                  'states': sorted_states,
                  'code': code,
                  })


def register_with_state(request, state, code=None):
    """
    Allows users to select a school (in state) from dropdown list

    :param request: request to render page
    :param state: the standard state abbreviation, capitalized
    :param code: optional param which indicates a referral
    :return: page which allows user to select school from dropwdown
        OR redirect to a school page
    """
    try:
        school = request.POST['school']
    except MultiValueDictKeyError:
        schools = []
        for s in School.objects.filter(state=state):
            schools.append(s)
        schools = sorted(schools, key=lambda sch: sch.name)
        return render(request, 'CERN/register_state.html',
                      {
                      'state': STATES[state],
                      'abbr': state,
                      'schools': schools,
                      'code': code,
                      })
    else:
        if code:
            return HttpResponseRedirect("/CERN/%s/%s/%s"
                                        % (state, school, code))
        return HttpResponseRedirect("/CERN/%s/%s/" % (state, school))


def school(request, state, school_name, code=None):
    """
    Displays the school splash page

    :param request: request to render page
    :param state: standard state abbreviation of where school is
    :param school_name: name of school
        spaces may be replaced by _ in this param
    :param code: optional param which indicates a referral
    :return: rendering of school page or error page if no School with
        name and state combination can be found
    """
    referrer = None

    if code:
        try:
            referrer = Student.objects.get(referral_code=code)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/CERN/%s/%s/' % (state, school_name))

    try:
        school = School.objects.get(state=state.upper(),
                                    name=school_name.replace('_', ' '))
    except ObjectDoesNotExist:
        return render(request, 'CERN/no-school.html')
    else:
        try:
            head = school.get_head_student()
        except ObjectDoesNotExist:
            head = None
        return render(request, 'CERN/school_splash.html',
                      {
                      'school': school,
                      'head': head,
                      'referrer': referrer,
                      })


def save_school_logo(request, state, school_name):
    """
    Associates a recently-uploaded logo with a school

    :param request: POST request with uploaded image data
    :param state: standard state abbreviation for location of school
    :param school_name: name of school
    :return: a blank HttpResponse object if success on POST request
        OR an HttpResponseNotAllowed object (code 405)
    """
    if request.method == 'POST':
        school = School.objects.get(state=state, name=school_name)

        request_logo = request.POST.getlist('logo[]')
        logo_id = request_logo[0].split('/')[3]
        logo = UploadedFile.objects.get(pk=logo_id)
        school.logo = logo

        school.save()

        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


def save_school(request, state, school_name):
    """
    Updates school mascot and description

    :param request: POST request with mascot and description
    :param state: standard state abbreviation for location of school
    :param school_name: name of school
    :return: a blank HttpResponse if success on POST request
        OR an HttpResponseNotAllowed object (code 405)
    """

    if request.method == 'POST':
        school = School.objects.get(state=state, name=school_name)

        mascot = request.POST['mascot']
        if mascot != '':
            school.mascot = mascot

        description = request.POST['description']
        school.description = description

        school.save()

        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])


def import_school_data(request):
    """
    (Re)loads all schools from schools.csv into database

    Should only be used in the queue

    :param request: request to run import script
    :return: HttpResponseNotAllowed (code 405) if not POST request
    """
    if request.method == 'POST':
        import_schools()
    else:
        return HttpResponseNotAllowed(['POST'])


#todo: (after 6/20 release) prevent non-students from seeing page
@login_required
def dashboard(request):
    """
    Displays the CERN dashboard/scoreboard

    :param request: request to render page
    :return: dashboard customized for logged in student
    """
    student = Student.objects.get(user=request.user)

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


    return render(request, 'CERN/dashboard.html',
                  {
                  'student': student,
                  'content': content,
                  'design': design,
                  'qa': qa,
                  })


@login_required
def social_media(request):
    """
    Displays social media page with referral links and basic info

    :param request: request to render page
    :return: social media page customized for currently logged in
        student (with custom links and info on top 5 referred users)
    """
    student = Student.objects.get(user=request.user)

    referrals = sorted(student.referrals(), key=lambda s: s.rep())
    num_referred = len(referrals)
    need_saving = False

    if student.same_school_referral_url and student.referral_url:
        referral_url = student.referral_url
        same_referral_url = student.same_school_referral_url
    else:
        referral_url = ('http://' + request.META['HTTP_HOST'] +
                        '/CERN/register/%s' % student.referral_code)
        same_referral_url = ('http://' + request.META['HTTP_HOST'] +
                             '/CERN/%s/%s/%s' % (student.school.state,
                                                 student.school.name,
                                                 student.referral_code))
        need_saving = True

    referred1 = referred2 = referred3 = referred4 = referred5 = None

    try:
        referred1 = referrals[0]
    except IndexError:
        pass
    else:
        try:
            referred2 = referrals[1]
        except IndexError:
            pass
        else:
            try:
                referred3 = referrals[2]
            except IndexError:
                pass
            else:
                try:
                    referred4 = referrals[3]
                except IndexError:
                    pass
                else:
                    try:
                        referred5 = referrals[4]
                    except IndexError:
                        pass

    return render(request, 'CERN/social_media.html',
                  {
                  'num_referred': num_referred,
                  'referral_url': referral_url,
                  'same_referral_url': same_referral_url,
                  'student': student,
                  'need_saving': need_saving,
                  'referred1': referred1,
                  'referred2': referred2,
                  'referred3': referred3,
                  'referred4': referred4,
                  'referred5': referred5,
                  })


@login_required
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
    return render(request, 'CERN/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  })


@login_required
def design(request):
    """
    Displays design page

    :param request: request to render page
    :return: 'Coming Soon' page customized for design
    """
    project = 'Sponsor Page Design'
    joined = None
    try:
        mailing = MailingList.objects.get(project=project)
    except ObjectDoesNotExist:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  })


@login_required
def testing(request):
    """
    Displays QA testing page

    :param request: request to render page
    :return: 'Coming Soon' page customized for QA testing
    """
    project = 'Quality Assurance Testing'
    joined = None
    try:
        mailing = MailingList.objects.get(project=project)
    except ObjectDoesNotExist:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  })


@login_required
def mobile(request):
    """
    Displays Mobile page

    :param request: request to render page
    :return: 'Coming Soon' page customized for Mobile
    """
    project = 'Mobile App'
    joined = None
    try:
        mailing = MailingList.objects.get(project=project)
    except ObjectDoesNotExist:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  })


def add_email_alert(request):
    """
    Adds an email address to a MailingList for a give project

    :param request: HttpRequest that should include 'project' and
        'email' in POST data
    :return: Blank HttpResponse on success
        OR HttpReponseNotAllowed (code 405) if not POST request
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
        student = Student.objects.get(user=request.user)
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


def amazon_login(request):
    """
    Either logs in student from Amazon or creates new Student object

    Slightly customized from accounts.views.amazon_login to add Student
        object creation (and hard-redirect to CERN dashboard)

    :param request: response from Amazon on successful login
        Should also include 'state' and 'school' params in GET
    :return: redirect to CERN dashboard or standard login page w/errors
    """
    error = request.GET.get('error', None)
    return_url = get_return_url(request)
    
    state = get_request_param(request, 'state')
    name = get_request_param(request, 'school')

    referrer_id = get_request_param(request, 'referrer')

    if error is not None:
        error_message = (request.GET.get('error_description') +
                         '<br><a href="' + request.GET.get('error_uri') +
                         '">Learn more</a>')
        return render(request, 'accounts/login.html', {
            'next': return_url,
            'error': error_message
        })

    access_token = request.GET.get('access_token')
    query_parameters = urllib.urlencode({'access_token': access_token})

    token_request = urllib2.urlopen('https://api.amazon.com/auth/O2/tokeninfo?%s'
                                    % query_parameters)
    json_data = json.load(token_request)
    if token_request.getcode() == 200:
        is_verified = json_data['aud'] == settings.AMAZON_LOGIN_CLIENT_ID
        if not is_verified:
            return render(request, 'accounts/login.html', {
                'next': return_url,
                'error': 'Verification failed! Please contact administrators'
            })

        profile_request = urllib2.urlopen(
            'https://api.amazon.com/user/profile?%s' % query_parameters)
        profile_json_data = json.load(profile_request)
        if profile_request.getcode() == 200:
            amazon_user_id = profile_json_data['user_id']
            amazon_user_name = profile_json_data['name']
            amazon_user_email = profile_json_data['email']

            user_profiles = UserProfile.objects.filter(amazon_id=amazon_user_id)
            if user_profiles.count() == 0:
                users_with_email = User.objects.filter(email=amazon_user_email)

                if len(users_with_email) == 0:
                    user = User.objects.create_user(amazon_user_email,
                                                    amazon_user_email, amazon_user_id)
                    user.save()
                else:  # User exists, but for some reason it's profile wasn't created
                    user = users_with_email[0]

                user_profile = UserProfile(user=user)
                user_profile.amazon_id = amazon_user_id
                user_profile.amazon_access_token = access_token
                user_profile.username = amazon_user_name
                user_profile.save()

                # Set up Student object
                school = School.objects.get(name=name, state=state)
                student = Student(user=user, school=school)
                if school.num_students == 0:
                    student.isHead = True

                student.save()

                # Referral points have to come after save, so put all
                 # the referral stuff together
                if referrer_id is not '':
                    referrer = Student.objects.get(id=referrer_id)
                    student.referred_by = referrer.user
                    student.save()

                    recruited_new_student(referrer, school)

            user = authenticate(username=amazon_user_email, password=amazon_user_id)
            profile = user.get_profile()

            if not profile.amazon_access_token:
                profile.amazon_access_token = access_token
                profile.save()

            login(request, user)

            return HttpResponseRedirect('/CERN/')
        else:
            return _handle_amazon_conn_error(request, profile_json_data)
    else:
        return _handle_amazon_conn_error(request, json_data)


def disable_about(request):
    """
    Disables 'about X' part of given page for given student

    :param request: request to disable about, should include 'about'
        param which specifies which 'about' to hide
    :return: a blank HttpResponse on success
    """
    student = Student.objects.get(user=request.user)
    about = request.POST['about']
    if about == 'CERN':
        student.show_CERN = False
    elif about == 'social media':
        student.show_social_media = False
    student.save()

    return HttpResponse()
