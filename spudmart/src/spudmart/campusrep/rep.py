from spudmart.campusrep.models import Student, School
from spudmart.venues.models import Venue

# Rep values for the following tasks:
RECRUITED_HEAD = 30
RECRUITED_NEW_MAX = 20
RECRUITED_NEW_MIN = 2
COMPLETE_PAGE = 10
PAGE_LIKE = 2
PAGE_SHARE = 3
FILTERED_OUT = 5
SPUD = 10
ADD_TEAM = 10
INAPPROPRIATE = -15
SHORT_DELAY = -5
MEDIUM_DELAY = -10
IGNORED = -15

def add_venue_rep(venue, points):
    '''Adds to (or subtracts from) the reputation score of a venue.
    Also updates the rep of the venue's owner.'''
    venue.rep += points
    student = Student.objects.get(user = venue.user)
    add_student_rep(student, points)

def add_student_rep(student, points):
    '''Adds to (or subtracts from) the reputation score of a student.
    Also updates the rep of the student's school.'''
    student.rep += points
    school = student.school
    add_school_rep(school, points)

def add_school_rep(school, points):
    '''Adds to (or subtracts from) the reputation score of a school.'''
    school.rep += points

def recuited_new_head_student(recruiter):
    add_student_rep(recruiter, RECRUITED_HEAD)

def recruited_new_student(recruiter, recruited_school):
    # To get 20 points for the 2nd student, and so on down the line
    points = (RECRUITED_NEW_MAX + 2) - recruited_school.num_students
    if points < RECRUITED_NEW_MIN:
        points = RECRUITED_NEW_MIN
    add_student_rep(recruiter, points)
    
def get_head_student(school):
    try:
        stud = Student.objects.get(School=school, isHead=True)
#     There's two exceptions that can occur, none found and more than one found
    except Exception:
        return None
    else:
        return stud

def completed_page_info(pageholder):
    if isinstance(pageholder, Venue):
        add_venue_rep(pageholder, COMPLETE_PAGE)
    elif isinstance(pageholder, School):
        add_student_rep(get_head_student(pageholder), COMPLETE_PAGE)

def liked_page(pageholder):
    if isinstance(pageholder, Venue):
        add_venue_rep(pageholder, PAGE_LIKE)
    elif isinstance(pageholder, School):
        add_student_rep(get_head_student(pageholder), PAGE_LIKE)

def shared_page(pageholder):
    if isinstance(pageholder, Venue):
        add_venue_rep(pageholder, PAGE_SHARE)
    elif isinstance(pageholder, School):
        add_student_rep(get_head_student(pageholder), PAGE_SHARE)

def filtered_bad_post(venue):
    add_venue_rep(venue, FILTERED_OUT)

def created_spud(venue):
    add_venue_rep(venue, SPUD)

def added_team(venue):
    add_venue_rep(venue, ADD_TEAM)

def inappropriate_post(venue):
    add_venue_rep(venue, INAPPROPRIATE)

def short_post_delay(venue):
    add_venue_rep(venue, SHORT_DELAY)

def medium_post_delay(venue):
    add_venue_rep(venue, MEDIUM_DELAY)

def ignored_post(venue):
    add_venue_rep(venue, IGNORED)
