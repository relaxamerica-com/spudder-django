from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseNotAllowed
from spudmart.upload.models import UploadedFile
from spudmart.CERN.models import School, Student, STATES, MailingList
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from spudmart.CERN.utils import import_schools, strip_invalid_chars
from django.contrib.auth.decorators import login_required, user_passes_test
from spudmart.CERN.rep import recruited_new_student
from spudmart.utils.url import get_return_url
import settings


def user_is_student(user):
    """
    Determines whether user is associated with a student

    Helper method to use with user_passes_test view decorator

    :param user: any user
    :return: True if user is student and False if not
    """
    try:
        Student.objects.get(user=user)
    except ObjectDoesNotExist:
        return False
    else:
        return True


def register(request, referral_id=None):
    """
    Allows users to select a state from a dropdown list, to find school

    :param request: the request to render page
    :param code: optional param which indicates a referral
    :return: page where users can select state from a dropwdown list
    """
    sorted_states = sorted(STATES.items(), key=lambda x: x[1])
    
    if request.method == 'POST':
        return register_with_state(request, state=request.POST['state'],
                                   referral_id=referral_id)

    return render(request, 'CERN/register.html',
                  {
                  'states': sorted_states,
                  'referral_id': referral_id,
                  })


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
        return render(request, 'CERN/register_state.html',
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
            return HttpResponseRedirect('/cern/%s/%s/%s/' % (state, school_id,
                                                             name))

    try:
        school = School.objects.get(id=school_id)
    except ObjectDoesNotExist:
        return render(request, 'CERN/no-school.html')
    else:
        stripped_name = strip_invalid_chars(school.name)
        if strip_invalid_chars(school.name) != name:
            return HttpResponseRedirect('/cern/%s/%s/%s' % (state, school_id,
                                                            stripped_name))
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


def save_school_logo(request, school_id):
    """
    Associates a recently-uploaded logo with a school

    :param request: POST request with uploaded image data
    :param state: standard state abbreviation for location of school
    :param school_name: name of school
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

    Should only be used in the queue (it's protected anyway)

    :param request: request to run import script
    :return: HttpResponseNotAllowed (code 405) if not POST request
    """
    if request.method == 'POST':
        import_schools()
    else:
        return HttpResponseNotAllowed(['POST'])


def display_cern(request):
    """
    Displays either the CERN dashboard or a splash page about CERN.

    :param request: the request to render page
    :return: the dashboard if a student is logged in OR a splash page
        about CERN
    """
    if request.user.is_authenticated():
        try:
            Student.objects.get(user=request.user)
        except ObjectDoesNotExist:
            # In the future, we can create a custom "join CERN" page
            #  for existing users
            return cern_splash(request)
        else:
            return dashboard(request)
    else:
        return cern_splash(request)


def cern_splash(request):
    return render(request, 'CERN/splash.html')


@login_required
@user_passes_test(user_is_student, '/CERN/non-student/')
def dashboard(request):
    """
    Displays the CERN dashboard/scoreboard,

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
@user_passes_test(user_is_student, '/cern/non-student/')
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
                        '/cern/register/%s' % student.id)
        same_referral_url = ('http://' + request.META['HTTP_HOST'] +
                             '/cern/%s/register/%s' %
                             (student.school.id,
                             student.id))
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
    return render(request, 'CERN/coming_soon.html',
                  {
                  'project': project,
                  'joined': joined,
                  })


@login_required
@user_passes_test(user_is_student, '/cern/non-student/')
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
@user_passes_test(user_is_student, '/cern/non-student/')
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
@user_passes_test(user_is_student, '/cern/non-student/')
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
        return render(request, 'CERN/school-login.html',
                      {
                      'school': school,
                      'referrer': referrer,
                      })


def user_not_student_error_page(request):
    """
    Displays an error page when a non-student hits a private CERN page

    :param request: request to render the restricted page
    :return: a simple error page that links to the info page for CERN
    """
    return render(request, 'CERN/non-student.html')


def join_school(request, school_id, referral_id=None):
    """
    Makes an existing user into a Student, linked to the given school

    :param request: request to join school
    :param school_id: ID of school
    :return: redirect to school page
    """
    sch = School.objects.get(id=school_id)
    stu = Student(user=request.user, school=sch)

    if sch.num_students == 0:
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
    return render(request, 'CERN/login.html', {
                           'client_id': settings.AMAZON_LOGIN_CLIENT_ID,
                           'base_url': settings.SPUDMART_BASE_URL,
                           'returnURL': get_return_url(request)
    })