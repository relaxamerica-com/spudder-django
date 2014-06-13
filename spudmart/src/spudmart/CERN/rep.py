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

REFERRAL_MODIFIER = 2


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

    If student was referred by someone, adds points to referrer

    :param student: the student who owns the venue
    :param points: the amount points change
        can be positive or negative
    """

    student.marketing_points += points
    student.save()

    if student.referred_by is not None:
        referrer = Student.objects.get(user=student.referred_by)
        add_referral_points(referrer, points)


def add_social_media_points(student, points):
    """
    Adds to (or subtracts from) the social media points of a student.

    If student was referred by someone, adds points to referrer

    :param student: the student who performed the action
    :param points: the amount points change
        can be positive or negative
    """
    student.social_media_points += points
    student.save()

    if student.referred_by is not None:
        referrer = Student.objects.get(user=student.referred_by)
        add_referral_points(referrer, points)


def add_referral_points(referrer, points):
    """
    Adds a fraction of points awarded to referred student to referrer

    REFERRAL_MODIFIER sets what points is divided by

    :param referrer: the student who referred the student who performed
        an action which gains points
    :param points: the number of points given for performing the action
    """
    add_social_media_points(referrer, points / REFERRAL_MODIFIER)


def recruited_new_head_student(recruiter):
    """
    Adds points for recruiting new head student.

    :param recruiter: the student who did the recruiting
    """
    add_social_media_points(recruiter, RECRUITED_HEAD)


def recruited_new_student(recruiter, recruited_school):
    """
    Adds points for recruiting a new student after student is created.

    Values student based on the number of students already present at
        the school, from RECRUITED_NEW_MAX for the 2nd student down to
        a minimum of RECRUITED_NEW_MIN points.

    Correctly handles a head student being referred (more points are
        awarded for head student than RECRUITED_NEW_MAX)

    :param recruiter: the student who did the recruiting
    :param recruited_school: the school of the newly recruited student
    """

    # To get X points for the 2nd student, add 2 to max points
    num_students = recruited_school.num_students()
    if num_students == 0:
        recruited_new_head_student(recruiter)
    else:
        points = (RECRUITED_NEW_MAX + 2) - num_students
    
        if points < RECRUITED_NEW_MIN:
            points = RECRUITED_NEW_MIN
        
        add_social_media_points(recruiter, points)


def signed_up(new_student):
    """
    Rewards students with Social Media Points for signing up

    The student gets the same number of points as a recruiter would
     for recruiting the nth student at the new student's school

    If the student was recruited by someone, the recruiter does not get
     extra points for this action, as it is performed before that link
     has been created

    :param new_student: A new student which has already been saved
    """
    if new_student.isHead:
        add_social_media_points(new_student, RECRUITED_HEAD)
    else:
        num_students = new_student.school.num_students()
        points = RECRUITED_NEW_MAX - num_students
        points = max(RECRUITED_NEW_MIN, points)
        add_social_media_points(new_student, points)


def completed_page_info(pageholder):
    """
    Adds points for completing a venue/school page

    :param pageholder: the Venue or School whose splash page has been
        edited by the owner or head student, respectively
    """
    if isinstance(pageholder, Venue):
        add_venue_rep(pageholder, COMPLETE_PAGE)
    elif isinstance(pageholder, School):
        add_social_media_points(pageholder.get_head_student(), COMPLETE_PAGE)


def liked_page(pageholder):
    """
    Adds points for someone liking a venue/school page

    :param pageholder: the Venue or School whose page has been liked
    """
    if isinstance(pageholder, Venue):
        add_venue_rep(pageholder, PAGE_LIKE)
    elif isinstance(pageholder, School):
        add_social_media_points(pageholder.get_head_student(), PAGE_LIKE)


def shared_page(pageholder):
    """
    Adds points for a venue/school page being shared

    :param pageholder: the Venue or School whose page has been shared
    """
    if isinstance(pageholder, Venue):
        add_venue_rep(pageholder, PAGE_SHARE)
    elif isinstance(pageholder, School):
        add_social_media_points(pageholder.get_head_student(), PAGE_SHARE)


def filtered_bad_post(venue):
    """
    Rewards a venue (owner) for marking posts as not relevant

    :param venue: the venue related to the post that was ignored
    """
    add_venue_rep(venue, FILTERED_OUT)


def created_spud(venue):
    """
    Rewards a venue (owner) for publishing SPUDs

    :param venue: the venue related to the created SPUD
    """
    add_venue_rep(venue, SPUD)


def added_team(venue):
    """
    Rewards a venue (owner) for adding a team to a venue

    :param venue: the venue to which the team was added
    """
    add_venue_rep(venue, ADD_TEAM)


def inappropriate_post(venue):
    """
    Punishes a venue (owner) for creating an inappropriate post

    :param venue: the venue which had the inappropriate post
    """
    add_venue_rep(venue, INAPPROPRIATE)


def short_post_delay(venue):
    """
    Light punishment for a post published a few days after creation

    :param venue: the venue where the post was delayed
    """
    add_venue_rep(venue, SHORT_DELAY)


def medium_post_delay(venue):
    """
    Moderate punishment for a post published a while after creation

    :param venue: the venue where the post was delayed
    """
    add_venue_rep(venue, MEDIUM_DELAY)


def ignored_post(venue):
    """
    Severe punishment for never publishing a post

    :param venue: the venue where a post was ignored
    """
    add_venue_rep(venue, IGNORED)
