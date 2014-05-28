from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseNotAllowed
from spudmart.upload.models import UploadedFile
from spudmart.CERN.models import School, Student, STATES
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from spudmart.CERN.utils import import_schools

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
def school(request, state, school_name):
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

