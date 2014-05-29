from django.db import models
import uuid
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField
from django.db.models.fields import CharField

# 100 points to get from level 1 to 2 for venues
VENUE_REP_LEVEL_MODIFIER = 100
# 1000 points to get from level 1 to 2 for students/groundskeepers (10x venue requirement)
STUDENT_REP_LEVEL_MODIFIER = 1000
# 100000 points to get from level 1 to 2 for schools (10x student requirement)
SCHOOL_REP_LEVEL_MODIFIER = 100000

DEFAULT_CHALLENGE_DURATION = timedelta(days = 7)

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
    '''Calculates the largest "triangle number" less than the @param num supplied.
    "Triangle numbers" are 1, 3, 6, 10, etc. (add 1, add 2, add 3, etc.)
    Used to determine the level based on rep, after dividing by respective LEVEL_MODIFIER.
    '''
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
    num_students = models.IntegerField(default = 0)
    state = models.CharField(max_length = 2)
    mascot = models.CharField(max_length = 32, null = True)
    logo = models.ForeignKey(UploadedFile, null = True)
    description = models.TextField()
    
    def level(self):
        return get_max_triangle_num_less_than(self.get_rep() / SCHOOL_REP_LEVEL_MODIFIER)

    def __str__(self, *args, **kwargs):
        return self.name + ", " + str(self.num_students) + " students, " + str(self.get_rep()) + " rep"
    
    def __eq__(self, other):
        return self.pk == other.pk
    
    def get_rep(self):
        rep = 0
        for student in Student.objects.filter(school = self):
            rep += student.rep
        return int(rep)
    
    def get_students(self):
        ''' Convenience method which returns a standard list of students associated with
            the school.
        '''
        students = []
        for stud in Student.objects.filter(school = self):
            students.append(stud) 
        return students
    
    def get_head_student(self):
        return Student.objects.get(school = self, isHead = True)
    
    def verbose_state(self):
        return STATES[self.state]


class Student(models.Model):
    ''' A model for Student objects (Groundskeepers), which stores the standard Django 
        User object associated with the student, the school, whether the student is the
        Head Student, referral information, and the student's reputation.
        
        The database is indexed on User since that's how the students are most often looked up.
    '''    
    user = models.ForeignKey(User, unique = True, db_index = True, related_name="student_user")
    school = models.ForeignKey(School)
    isHead = models.BooleanField()
    
    referral_code = models.CharField(max_length=128, unique=True)
    referred_by = models.ForeignKey(User, blank=True, null=True, related_name="referred_by_user")
    
    rep = models.IntegerField(default = 0)
    
    

    def save(self, force_insert=False, force_update=False, using=None):
        ''' Default save method overwritten so that the School's student count is always
            accurate, and the student's referral_code is only assigned once.
        '''
        if self.pk is None:
            self.school.num_students += 1
            self.school.save()
            self.referral_code = str(uuid.uuid4())
            
        return models.Model.save(self, force_insert, force_update, using)

    def __str__(self):
        something = str(self.user.username)
        if self.isHead:
            something += ", Head at "
        else:
            something += ", at "
        something += str(self.school.name) + ", " + str(self.rep) + " rep points"
        return something

    def delete(self, using=None):
        ''' Default delete method overwritten so that deleting a student updates the
            school's count to reflect the loss of a student.
        '''
        self.school.num_students -= 1
        self.school.save()
        return models.Model.delete(self, using)

    def __eq__(self, other):
        return self.user == other.user
    
    def check_contest_head(self):
        ''' Method to determine whether a given student can contest the current "head student".
            Ensures that challenging student has more rep than head student.
        '''
        head_student = self.school.get_head_student()
        if not self.isHead and self.rep > head_student.rep:
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
            challenge = Challenge(challenger = self.school, challenged = school, challenge_end = datetime.utcnow() + challenge_durration)
            challenge.save()
            return challenge        
    
    def level(self):
        return get_max_triangle_num_less_than(self.rep / STUDENT_REP_LEVEL_MODIFIER)
    
    def add_rep(self, points):
        self.rep += points
        self.save()
        if self.referred_by:
            referrer = Student.objects.get(user = self.referred_by)
            referrer.add_rep(points)

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
    project = CharField()

    def __str__(self):
        return "%s, %s"%(self.project, self.emails)
