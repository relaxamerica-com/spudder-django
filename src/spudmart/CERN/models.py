from urllib2 import Request, urlopen
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField
from django.db.models.fields import CharField
from collections import OrderedDict

# 100 points to get from level 1 to 2 for venues
VENUE_REP_LEVEL_MODIFIER = 100
# 1000 points to get from level 1 to 2 for students/groundskeepers h
#(10x venue requirement)
STUDENT_REP_LEVEL_MODIFIER = 1000
# 100000 points to get from level 1 to 2 for schools
#(10x student requirement)
SCHOOL_REP_LEVEL_MODIFIER = 100000

DEFAULT_CHALLENGE_DURATION = timedelta(days=7)

STATES = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

SORTED_STATES = OrderedDict(sorted(STATES.items()))

STATUS_ACCEPTED = "accepted"
STATUS_REJECTED = "rejected"
STATUS_WAITLIST = "waitlist"


def get_max_triangle_num_less_than(num, n=1):
    """ Calculates the largest triangle number less than num.
    
    "Triangle numbers" are 1, 3, 6, 10,... (add 1, then 2, then 3, etc)
    Used to determine level based on rep points, after dividing by the
        respective LEVEL_MODIFIER constant
      
    Args:
        num: an integer
        n: also an integer, the order of the "triangle number"
            1st order: 1, 2nd order: 3, 3rd order: 6,...
    Returns:
        the greatest order of triangle number less than num
        denotes the "level" of reputation
    """
    tri = n*(n+1)/2
    if num/tri >= 1:
        n += 1
        return get_max_triangle_num_less_than(num, n)
    else:
        return n


class School(models.Model):
    """
        A model for School objects that stores a string literal of the school name and
        the number of students at the school.
        Due to errors with saving/updating rep points, rep is now calculated via method 
        which sums the rep points of all students associated with school. 
        Includes method which evaluates level based on reputation.
    """
    name = models.CharField(max_length=124, db_index=True)
    state = models.CharField(max_length=2)
    mascot = models.CharField(max_length=32, null=True)
    logo = models.ForeignKey(UploadedFile, null=True)
    description = models.TextField(default='')
    cover_image = models.ForeignKey(UploadedFile, null=True, related_name="school_cover_image")
    full_address = models.CharField(max_length=200, null=True)

    def level(self):
        return get_max_triangle_num_less_than(self.get_rep() / SCHOOL_REP_LEVEL_MODIFIER)

    def __str__(self, *args, **kwargs):
        return self.name + ", " + str(self.num_students()) + " students, " + str(self.get_rep()) + " rep"
    
    def __eq__(self, other):
        return self.pk == other.pk
    
    def get_rep(self):
        rep = 0
        for student in self.get_students():
            rep += student.rep()
        return int(rep)
    
    def get_students(self):
        """
        A list of all students associated w/school
        :return: a standard List object of all students
        """
        return Student.objects.filter(school=self)
    
    def get_head_student(self):
        try:
            s = Student.objects.get(school=self, isHead=True)
        except ObjectDoesNotExist:
            return None
        else:
            return s
    
    def verbose_state(self):
        return STATES[self.state]

    def marketing_points(self):
        points = 0
        for s in self.get_students():
            points += s.marketing_points
        return points

    def social_media_points(self):
        points = 0
        for s in self.get_students():
            points += s.social_media_points
        return points

    def content_points(self):
        points = 0
        for s in self.get_students():
            points += s.content_points
        return points

    def design_points(self):
        points = 0
        for s in self.get_students():
            points += s.design_points
        return points

    def testing_points(self):
        points = 0
        for s in self.get_students():
            points += s.testing_points
        return points

    def most_popular_project(self):
        marketing = self.marketing_points()
        social_media = self.social_media_points()
        content = self.content_points()
        design = self.design_points(),
        testing = self.testing_points()
        max_points = max(marketing, social_media, content, design, testing)

        if max_points != 0:
            if max_points == marketing:
                return 'Marketing: %s team pts' % max_points
            elif max_points == social_media:
                return 'Social Media PR: %s team pts' % max_points
            elif max_points == content:
                return 'Content Management: %s team pts' % max_points
            elif max_points == design:
                return 'Design: %s team pts' % max_points
            elif max_points == testing:
                return 'QA Testing: %s team pts' % max_points

        return 'No one has started a project yet! (0 team pts)'

    def num_students(self):
        return self.get_students().count()

    # def full_address(self):
    #     if self._full_address:
    #         return self._full_address
    #     else:
    #         return None
    # <<Address or something >>


class Student(models.Model):
    """
    A model for Student objects (Groundskeepers), which stores the standard Django
    User object associated with the student, the school, whether the student is the
    Head Student, referral information, and the student's reputation.
        
    The database is indexed on User since that's how the students are most often looked up.
    """
    user = models.ForeignKey(User, unique=True, db_index=True,
                             related_name="student_user")
    school = models.ForeignKey(School)
    isHead = models.BooleanField()
    
    referral_url = models.CharField(max_length=200, null=True)
    same_school_referral_url = models.CharField(max_length=200, null=True)
    
    referred_by = models.ForeignKey(User, blank=True, null=True,
                                    related_name="referred_by_user")
    referred_id = models.CharField(max_length=200, null=True)
    
    marketing_points = models.IntegerField(default=0)
    _venue_points = models.IntegerField(default=0)
    team_points = models.IntegerField(default=0)
    social_media_points = models.IntegerField(default=0)
    testing_points = models.IntegerField(default=0)
    content_points = models.IntegerField(default=0)
    design_points = models.IntegerField(default=0)

    show_CERN = models.BooleanField(default=True)
    show_social_media = models.BooleanField(default=True)

    linkedin_token = models.CharField(max_length=200, blank=True, null=True)
    linkedin_expires = models.DateTimeField(blank=True, null=True)
    auto_brag_marketing = models.BooleanField(default=False)
    auto_brag_social_media = models.BooleanField(default=False)
    level_brag_marketing = models.BooleanField(default=False)
    level_brag_social_media = models.BooleanField(default=False)

    info_messages_dismissed = models.TextField(blank=True, null=True)

    logo = models.ForeignKey(UploadedFile, null=True, related_name="student_logo")
    cover_image = models.ForeignKey(UploadedFile, null=True, related_name="student_cover_image")
    display_name = models.CharField(max_length=200, blank=True, null=True)
    append_points = models.BooleanField(default=False)

    linkedin_link = models.CharField(max_length=200, null=True)
    facebook_link = models.CharField(max_length=200, null=True)
    twitter_link = models.CharField(max_length=200, null=True)
    google_link = models.CharField(max_length=200, null=True)
    instagram_link = models.CharField(max_length=200, null=True)

    _qa_status = models.CharField(max_length=8, null=True)
    resume = models.TextField(null=True)
    applied_qa = models.BooleanField(default=False)

    @property
    def venue_points(self):
        return self.marketing_points + self._venue_points

    def __str__(self):
        something = str(self.user.username)
        if self.isHead:
            something += ", Team Captain for "
        else:
            something += ", "
        something += str(self.school.name)
        return something
    
    def check_contest_head(self):
        ''' Method to determine whether a given student can contest the current "head student".
            Ensures that challenging student has more rep than head student.
        '''
        head_student = self.school.get_head_student()
        if not self.isHead and self.rep() > head_student.rep():
            return True
        else:
            return False
    
    def replace_head(self):
        ''' Replaces existing head student with current student. '''
        head_student = self.school.get_head_student()
        head_student.isHead = False
        head_student.save()
        
        self.isHead = True
        self.save()
        
    def issue_challenge(self, school, challenge_durration = DEFAULT_CHALLENGE_DURATION):
        ''' Method used to issue a challenge to another school. 
            Can only be invoked by a Head Student.
            
            Parameter challenge_duration must be a timedelta object. 
        '''
        if self.isHead:
            challenge = Challenge(challenger=self.school,
                                  challenged=school,
                                  challenge_end=datetime.utcnow() +
                                                challenge_durration)
            challenge.save()
            return challenge        
    
    def level(self):
        return get_max_triangle_num_less_than(self.rep() /
                                              STUDENT_REP_LEVEL_MODIFIER)

    def rep(self):
        points = (self.venue_points + self.team_points +
                  self.social_media_points + self.testing_points +
                  self.content_points + self.design_points)
        return points
    
    def top_project(self):
        max_points = max(self.venue_points, self.team_points,
                         self.social_media_points, self.testing_points,
                         self.content_points, self.design_points)
        if max_points != 0:
            if max_points == self.venue_points:
                return 'Marketing (Venues)'
            elif max_points == self.team_points:
                return 'Marketing (Teams)'
            elif max_points == self.social_media_points:
                return 'Social Media'
            elif max_points == self.testing_points:
                return 'Testing'
            elif max_points == self.content_points:
                return 'Content'
            elif max_points == self.design_points:
                return 'Design'

        return 'No Project Started'

    def referrals(self):
        students = []
        for s in Student.objects.filter(referred_id=self.id):
            students.append(s)
        return students

    def top_project_verbose(self):
        max_points = max(self.venue_points, self.team_points,
                         self.social_media_points, self.testing_points,
                         self.content_points, self.design_points)
        if max_points != 0:
            if max_points == self.venue_points:
                return 'Marketing - Venues (%s pts)' % max_points
            elif max_points == self.team_points:
                return 'Marketing - Teams (%s pts)' % max_points
            elif max_points == self.social_media_points:
                return 'Social Media (%s pts)' % max_points
            elif max_points == self.content_points:
                return 'Content (%s pts)' % max_points
            elif max_points == self.design_points:
                return 'Design (%s pts)' % max_points
            elif max_points == self.testing_points:
                return 'Testing (%s pts)' % max_points

        return 'No Project Started (0 pts)'

    def hidden_info_messages(self):
        return (self.info_messages_dismissed or '').split(',')

    def dismiss_info_message(self, message_id):
        self.info_messages_dismissed = "%s,%s" % (self.info_messages_dismissed or '', message_id)
        self.save()

    def brag(self, comment):
        """
        Makes a post to LinkedIn with the supplied comment.

        :param comment: a string version of the HTML for the post
        :return: the response from the LinkedIn API
        """
        data = ("<?xml version='1.0' encoding='UTF-8'?>" +
                "<share><comment>" + comment +
                "</comment><visibility><code>anyone" +
                "</code></visibility></share>")

        request = Request('https://api.linkedin.com/v1/people/~/shares' +
                          '?oauth2_access_token=%s' % self.linkedin_token)
        request.add_header('Content-Type', 'application/xml')
        request.add_data(data)
        url = request.get_full_url()

        return urlopen(request).read()

    def brag_venue(self):
        """
        Posts the student's current marketing score to LinkedIn.

        :return: the response from the LinkedIn API
        """
        points = self.venue_points
        return self.brag("My score for Marketing Venues as a part of " +
                         "CERN on Spudder is now %s points." % points)

    def brag_social_media(self):
        """
        Post the student's current social media score to LinkedIn.

        :return: the response from the LinkedIn API
        """
        points = self.social_media_points
        return self.brag("My score for the Social Media PR project as a " +
                         "part of CERN on Spudder is now %s points." % points)

    def venue_level(self):
        """
        Determines the marketing level of the student.

        Levelling occurs at 1050, 2050, 3050, etc.
        Students start at Level 1 in any project where they have at
            least 1 point. 0 points = Level 0

        :return: an integer representing the level.
        """
        points = self.venue_points
        if points < 50:
            if points == 0:
                return 0
            else:
                return 1
        else:
            return ((points - 50) / 1000) + 1

    def social_media_level(self):
        """
        Determines the social media level of the student.

        Levelling occurs at 1050, 2050, 3050, etc.
        Students start at Level 1 in any project where they have at
            least 1 point. 0 points = Level 0

        :return: an integer representing the level.
        """
        points = self.social_media_points
        if points < 50:
            if points == 0:
                return 0
            else:
                return 1
        else:
            return ((points - 50) / 1000) + 1

    def brag_venue_level(self):
        """
        Sends a post to LinkedIn about the new Marketing (Venue) level.

        :return: the response from the LinkedIn Share API
        """
        return self.brag("I just reached Level " + str(self.marketing_level()) +
                         " in Marketing Venues for CERN on Spudder.")

    def brag_social_media_level(self):
        """
        Sends a post to LinkedIn about the new Social Media level.

        :return: the response from the LinkedIn Share API
        """
        return self.brag("I just reached Level " + str(self.social_media_level()) +
                         " in Social Media PR for CERN on Spudder.")

    def on_qa_waitlist(self):
        """
        Boolean whether student is on QA wait list
        :return: True or False
        """
        return self._qa_status == STATUS_WAITLIST

    def is_tester(self):
        """
        Boolean whether student is tester
        :return: True or False
        """
        return self._qa_status == STATUS_ACCEPTED

    def qa_status(self):
        """
        Accessor for _qa_status variable
        :return: a STATUS_ string, or False if no status
        """
        if self._qa_status:
            return self._qa_status
        else:
            return False


class Challenge(models.Model):
    ''' Stores information about challenges between schools based purely on rep points. 
        Stores the time when the challenge ends and the two schools involved.
    '''
    # The school issuing the challenge
    challenger = models.ForeignKey(School, related_name="challenging_school")
    # The school being challenged
    challenged = models.ForeignKey(School, related_name="challenged_school")
    
    challenge_end = models.DateTimeField()

    def determine_winner(self):
        if self.challenger.get_rep() > self.challenged.get_rep():
            return self.challenger
        elif self.challenged.get_rep() > self.challenger.get_rep():
            return self.challenged
        else:
            # It's a tie, so no one won
            return None

    def __str__(self, *args, **kwargs):
        return "Issued by %s on %s; %s is in the lead." %(self.challenger.name, self.challenged.name, self.determine_winner().name)
    
    def am_winning(self, school):
        ''' Convenience method to determine whether the supplied school is in the lead.
            Returns True if the school is winning, False if the team is not, and None if
            the school is not in the challenge.
        '''
        winner = self.determine_winner()
        if winner == school:
            return True
        elif school in [self.challenger, self.challenged]:
            return False
        else:
            return None


class MailingList(models.Model):
    emails = ListField()
    project = CharField(max_length=200)

    def __str__(self):
        return "%s, %s" % (self.project, self.emails)
