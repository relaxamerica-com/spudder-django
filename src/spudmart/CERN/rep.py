# from spudderdomain.models import TeamAdministrator
from spudmart.CERN.models import Student

# Rep values for various tasks, grouped like the methods

RECRUITED_HEAD = 30
RECRUITED_NEW_MAX = 20
RECRUITED_NEW_MIN = 2

REFERRAL_MODIFIER = 5

PAGE_LIKE = 2
PAGE_SHARE = 3
FILTERED_OUT = 5
SPUD = 10
ADD_TEAM = 10
INAPPROPRIATE = -15
SHORT_DELAY = -5
MEDIUM_DELAY = -10
IGNORED = -15

CREATED_VENUE = 5
BASIC_INFO = 1
VIDEO = 10
PHOTOS = 3
LOGO = 2

CREATED_TEAM = 5
FOLLOWER = 2
TEAM_VENUE_ASSOCIATED = 10
TEAM_SPUD = 1


#Basic rep modifying methods
def add_venue_rep(venue, points):
    """
    Adds to (or subtracts from) the reputation score of a venue.

    :param venue: the venue whose rep is to be changed
    :param points: the amount rep changes
        can be positive or negative
    """
    venue.rep += points
    venue.save()


    add_venue_points(venue.student, points)


def add_venue_points(student, points):
    """
    Adds to (or subtracts from) the marketing points of a student.

    If student was referred by someone, adds points to referrer.
    Also checks if the student is due for an "auto-brag".

    :param student: the student who owns the venue
    :param points: the amount points change
        can be positive or negative
    """
    old_level = student.venue_level()
    student._venue_points += points
    student.save()

    if student.referred_id is not None:
        referrer = Student.objects.get(id=student.referred_id)
        add_referral_points(referrer, points)

    # Check if student should auto-brag
    if student.auto_brag_marketing:
        if student.venue_points % 100 < points:
            student.brag_venue()

    # Check level bragging
    if student.level_brag_marketing:
        if old_level < student.venue_level():
            student.brag_venue_level()


def add_team_points(student, points):
    """
    Adds to (or subtracts from) the marketing points of a student.

    If student was referred by someone, adds points to referrer.

    :param student: the student who owns the team
    :param points: the amount points change
        can be positive or negative
    """
    student.team_points += points
    student.save()

    if student.referred_id is not None:
        referrer = Student.objects.get(id=student.referred_id)
        add_referral_points(referrer, points)

def add_social_media_points(student, points):
    """
    Adds to (or subtracts from) the social media points of a student.

    If student was referred by someone, adds points to referrer.
    Also checks if the student is due for an "auto-brag".

    :param student: the student who performed the action
    :param points: the amount points change
        can be positive or negative
    """
    old_level = student.social_media_level()
    student.social_media_points += points
    student.save()

    if student.referred_id is not None:
        referrer = Student.objects.get(user=student.referred_id)
        add_referral_points(referrer, points)

    # Check if student should auto-brag
    if student.auto_brag_social_media:
        if student.social_media_points % 100 < points:
            student.brag_social_media()

    # Check level bragging
    if student.level_brag_social_media:
        if old_level < student.social_media_level():
            student.brag_social_media_level()


def add_referral_points(referrer, points):
    """
    Adds a fraction of points awarded to referred student to referrer

    REFERRAL_MODIFIER sets what points is divided by

    :param referrer: the student who referred the student who performed
        an action which gains points
    :param points: the number of points given for performing the action
    """
    add_social_media_points(referrer, points / REFERRAL_MODIFIER)


# Recruiting/signup rep modifiers

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
    if num_students == 1:
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
        points = (RECRUITED_NEW_MAX + 2) - num_students
        points = max(RECRUITED_NEW_MIN, points)
        add_social_media_points(new_student, points)


# Venue rep methods

def liked_page(venue):
    """
    Rewards venue (owner) when anyone likes venue page

    :param venue: the Venue whose page has been liked
    """
    add_venue_rep(venue, PAGE_LIKE)


def shared_page(venue):
    """
    Reward venue (owner) when anyone shares venue page

    :param venue: the Venue whose page has been shared
    """
    add_venue_rep(venue, PAGE_SHARE)


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


def created_venue(student):
    """
    Rewards a student for creating a venue.

    :param student: the student who created the venue
    """
    add_venue_points(student, CREATED_VENUE)


def added_basic_info(venue):
    """
    Rewards a venue (and owner) when owner adds basic info to page.

    This method is used when the owner adds a common or sponsor name,
        or adds details about parking, playing surface, restrooms,
        concessions, admissions/seating, shelters, nearby medical
        centers, or accessibility.

    :param venue: the venue whose info was added
    """
    add_venue_rep(venue, BASIC_INFO)


def added_video(venue):
    """
    Rewards a venue (and owner) when owner adds a video to page.

    :param venue: the venue that received a video
    """
    add_venue_rep(venue, VIDEO)


def added_photos(venue):
    """
    Rewards a venue (and owner) when owner adds initial photos to page.

    :param venue: the venue that received image(s)
    """
    add_venue_rep(venue, PHOTOS)


def added_logo(venue):
    """
    Rewards a venue (and owner) when owner adds a custom logo to page.

    :param venue: the venue that got the logo
    """
    add_venue_rep(venue, LOGO)


def deleted_venue(venue):
    """
    Punishes a user for deleting a venue.

    This removes all the points that the student has earned from
        managing the venue.
    :param venue: The venue about to be deleted.
    """
    add_venue_points(venue.student, -venue.rep)


def created_team(student):
    """
    Rewards a student for creating a team.
    :param student: any Student
    """
    add_team_points(student, CREATED_TEAM)


def team_gained_follower(student):
    """
    Rewards a student when their team gains a follower.

    :param student: the student who manages team
    """
    add_team_points(student, FOLLOWER)


def team_associated_with_venue(student):
    """
    Rewards a student when they associate their team with a venue

    :param student: the student who manages the team
    """
    add_team_points(student, TEAM_VENUE_ASSOCIATED)


def team_tagged_in_spud(student):
    """
    Rewards a student when anyone tags their team in a SPUD.

    :param student: the student who manages the team
    """
    add_team_points(student, TEAM_SPUD)