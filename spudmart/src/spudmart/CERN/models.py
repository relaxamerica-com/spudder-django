from django.db import models
import uuid
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField
from django.db.models.fields import CharField

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
    ''' A model for School objects that stores a string literal of the school name and 
        the number of students at the school.
        Due to errors with saving/updating rep points, rep is now calculated via method 
        which sums the rep points of all students associated with school. 
        Includes method which evaluates level based on reputation. 
    ''' 
    name = models.CharField(max_length=124)
    state = models.CharField(max_length=2)
    mascot = models.CharField(max_length=32, null=True)
    logo = models.ForeignKey(UploadedFile, null=True)
    description = models.TextField(default='')
    
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
        ''' Convenience method which returns a standard list of students associated with
            the school.
        '''
        students = []
        for stud in Student.objects.filter(school=self):
            students.append(stud) 
        return students
    
    def get_head_student(self):
        return Student.objects.get(school=self, isHead=True)
    
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
        return len(self.get_students())


class Student(models.Model):
    ''' A model for Student objects (Groundskeepers), which stores the standard Django 
        User object associated with the student, the school, whether the student is the
        Head Student, referral information, and the student's reputation.
        
        The database is indexed on User since that's how the students are most often looked up.
    '''    
    user = models.ForeignKey(User, unique=True, db_index=True,
                             related_name="student_user")
    school = models.ForeignKey(School)
    isHead = models.BooleanField()
    
    referral_url = models.CharField(max_length=200, null=True)
    same_school_referral_url = models.CharField(max_length=200, null=True)
    
    referred_by = models.ForeignKey(User, blank=True, null=True,
                                    related_name="referred_by_user")
    
    marketing_points = models.IntegerField(default=0)
    social_media_points = models.IntegerField(default=0)
    content_points = models.IntegerField(default=0)
    design_points = models.IntegerField(default=0)
    testing_points = models.IntegerField(default=0)
    
    show_CERN = models.BooleanField(default=True)
    show_social_media = models.BooleanField(default=True)

    info_messages_dismissed = models.TextField(blank=True, null=True)

    def __str__(self):
        something = str(self.user.username)
        if self.isHead:
            something += ", Team Captain for "
        else:
            something += ", "
        something += str(self.school.name)
        return something

    def __eq__(self, other):
        return self.user == other.user
    
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
        points = (self.marketing_points + self.social_media_points +
                  self.content_points + self.design_points + 
                  self.testing_points)
        return points
    
    def top_project(self):
        max_points = max(self.marketing_points, self.social_media_points,
                         self.content_points, self.design_points,
                         self.testing_points)
        if max_points != 0:
            if max_points == self.marketing_points:
                return 'Marketing'
            elif max_points == self.social_media_points:
                return 'Social Media'
            elif max_points == self.content_points:
                return 'Content'
            elif max_points == self.design_points:
                return 'Design'
            elif max_points == self.testing_points:
                return 'Testing'

        return 'No Project Started'

    def referrals(self):
        students = []
        for s in Student.objects.filter(referred_by=self.user):
            students.append(s)
        return students

    def top_project_verbose(self):
        max_points = max(self.marketing_points, self.social_media_points,
                         self.content_points, self.design_points,
                         self.testing_points)
        if max_points != 0:
            if max_points == self.marketing_points:
                return 'Marketing (%s pts)' % max_points
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
    project = CharField(max_length = 200)

    def __str__(self):
        return "%s, %s"%(self.project, self.emails)
