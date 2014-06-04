from spudmart.CERN.models import Student, School
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
    """
    Adds to (or subtracts from) the reputation score of a venue.

    :param venue: the venue whose rep is to be changed
    :param points: the amount rep changes
        can be positive or negative
    """
    venue.rep += points
    venue.save()

    student = Student.objects.get(user=venue.user)
    add_marketing_points(student, points)

def add_marketing_points(student, points):
    """
    Adds to (or subtracts from) the marketing points of a student.

    :param student: the student who owns the venue
    :param points: the amount rep changes
        can be positive or negative
    """

    student.marketing_points += points

# def recruited_new_head_student(recruiter):
#     add_student_rep(recruiter, RECRUITED_HEAD)

def recruited_new_student(recruiter, recruited_school):
    # To be called AFTER a new student is recruited -- once the student object has been saved.
    
    # To get 20 points for the 2nd student, and so on down the line
    points = (RECRUITED_NEW_MAX + 2) - recruited_school.num_students
    
    # Ensure at least the minimum value for a new student is added
    if points < RECRUITED_NEW_MIN:
        points = RECRUITED_NEW_MIN
        
    add_student_rep(recruiter, points)
    
def get_head_student(school):
    try:
        stud = Student.objects.get(school=school, isHead=True)
#     There's two exceptions that can occur, none found and more than one found
    except Exception as e:
        print e
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
