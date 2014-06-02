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

def register(request, code = None):
    sorted_states = sorted(STATES.items(), key = lambda x:x[1])
    
    if request.method == 'POST':
        return register_with_state(request, state = request.POST['state'], code = code)    

    return render(request, 'CERN/register.html', { 
                                                    'states' : sorted_states, 
                                                    'code' : code, 
                                                    })

def register_with_state(request, state, code = None):
    try:
        school = request.POST['school']
    except MultiValueDictKeyError:
        schools = []
        for s in School.objects.filter(state = state):
            schools.append(s)
        schools = sorted(schools, key = lambda sch: sch.name)
        return render(request, 'CERN/register_state.html', { 
                                                              'state' : STATES[state], 
                                                              'abbr' : state, 
                                                              'schools' : schools,
                                                              'code' : code,
                                                              })
    else:
        if code:
            return HttpResponseRedirect("/CERN/%s/%s/%s"%(state, school, code))
        return HttpResponseRedirect("/CERN/%s/%s/"%(state, school))
        

def register_school(request, state, school_name, code = None):
    referrer = None
    if code:
        referrer = Student.objects.get(referral_code = code)
    try:
        school = School.objects.get(state = state.upper(), name = school_name.replace('_', ' '))
    except:
        # Later point to better error page
        return HttpResponse("Error")
    else:
        errors = []
        if request.method == 'POST':
            username = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 != password2:
                errors.append('Passwords did not match')
            else:
                # We should do checking to see if the user has already registered
                user = User.objects.create_user(username, username, password1)
                user.save()
                
                # Create the student
                student = Student(user = user, school = school)
                
                # Add referral info if it exists
                try:
                    code = request.POST['code']
                except MultiValueDictKeyError:
                    pass
                else:
                    stud = Student.objects.get(referral_code = code)
                    student.referred_by = stud.user
                    
                # See if the school needs a head student, and if so assign this student
                try:
                    school.get_head_student()
                except ObjectDoesNotExist:
                    student.isHead = True
                
                student.save()
                
                return HttpResponseRedirect('/venues/login')
        
        return render(request, 'CERN/school_register.html', { 
                                                               'errors' : errors , 
                                                               'school': school, 
                                                               'referrer' : referrer, 
                                                               'code' : code,
                                                               })

# School splash page
def school(request, state, school_name, code=None):
    try:
        school = School.objects.get(state = state.upper(), name = school_name.replace('_', ' '))
    except:
        # Later point to better error page
        return HttpResponse("Error")
    else:
        try:
            head = school.get_head_student()
        except ObjectDoesNotExist:
            return render(request, 'CERN/school_splash.html', { 'school': school })
        else:
            return render(request, 'CERN/school_splash.html', { 
                                                                 'school': school,
                                                                 'head' : head,
                                                                 'code' : code,
                                                                  })
            
# Customize school splash page
def save_school(request, state, school_name):
    """
    Updates school mascot and logo.
    
    Args:
        request: the HttpRequest object, should contain POST data including
            the logo and mascot to be updated
        state: the state in which the school is located, to find school in db 
        school_name: the name of the school, to find school in db
    Returns:
        if POST request: A blank HttpResponse object (code 200)
        if not: a HttpResponseNotAllowed object (code 405)
    """
    
    if request.method == 'POST':
        school = School.objects.get(state=state, name=school_name)
        
        # For logo
        request_logo = request.POST.getlist('logo[]')
        if len(request_logo):
            logo_id = request_logo[0].split('/')[3]
            logo = UploadedFile.objects.get(pk = logo_id)
            school.logo = logo
        
        # For mascot
        mascot = request.POST['mascot']
        if mascot != '':
            school.mascot = mascot
            
        description = request.POST['description']
        print description
        school.description = description
            
        school.save()
        
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST']) 
    

def import_school_data(request):
    if request.method == 'POST':
        import_schools()
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def dashboard(request):
    return render(request, 'CERN/dashboard.html')

@login_required
def social_media(request):
    student = Student.objects.get(user = request.user )
    num_referred = len(Student.objects.filter(referred_by = request.user))
    need_saving = False
    
    if student.same_school_referral_url and student.referral_url:
        referral_url = student.referral_url
        same_referral_url = student.same_school_referral_url
    else:
        referral_url = ('http://' + request.META['HTTP_HOST'] + 
                       '/CERN/register/%s'%student.referral_code)
        same_referral_url = ('http://' + request.META['HTTP_HOST'] + 
                             '/CERN/%s/%s/register/%s'%(student.school.state, 
                                                        student.school.name, 
                                                        student.referral_code))
        need_saving = True
        
    return render(request, 'CERN/social_media.html', 
                  {
                   'num_referred' : num_referred,
                   'referral_url' : referral_url,
                   'same_referral_url' : same_referral_url,
                   'student' : student,
                   'need_saving' : need_saving,
                  })
@login_required
def content(request):
    project = 'Blogging'
    joined = None
    try:
        mailing = MailingList.objects.get(project = project)
    except:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  { 'project' : project, 'joined' : joined, })

@login_required
def design(request):
    project = 'Sponsor Page Design'
    joined = None
    try:
        mailing = MailingList.objects.get(project = project)
    except:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  { 'project' : project, 'joined' : joined, })

@login_required
def testing(request):
    project = 'Quality Assurance Testing'
    joined = None
    try:
        mailing = MailingList.objects.get(project = project)
    except:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  { 'project' : project, 'joined' : joined, })

@login_required
def mobile(request):
    project = 'Mobile App'
    joined = None
    try:
        mailing = MailingList.objects.get(project = project)
    except:
        pass
    else:
        if request.user.email in mailing.emails:
            joined = True
        else:
            joined = False
    return render(request, 'CERN/coming_soon.html',
                  { 'project' : project, 'joined' : joined, })
    
def add_email_alert(request):
    if request.method == 'POST':
        try:
            mailinglist = MailingList.objects.get(project = request.POST['project'])
        except ObjectDoesNotExist:
            mailinglist = MailingList(emails = [], project = request.POST['project'])
        
        mailinglist.emails.append(request.POST['email'])
        mailinglist.save()
        return HttpResponse("Added user to list.")
    else:
        return HttpResponseNotAllowed(['POST'])
    
def save_my_short_urls(request):
    if request.method == 'POST':
        student = Student.objects.get(user = request.user)
        student.same_school_referral_url = request.POST['same_school_referral_url']
        student.referral_url = request.POST['referral_url']
        student.save()
        return HttpResponse("Success.")
    else:
        return HttpResponseNotAllowed(['POST'])