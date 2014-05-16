from django.contrib.auth.models import User
from django.db import models
import uuid


STUDENT_REP_LEVEL_MODIFIER = 1000
SCHOOL_REP_LEVEL_MODIFIER = 100000


def get_max_triangle_num_less_than(num, n=1):
    tri = n*(n+1)/2
    if num/tri > 1:
        n += 1
        return get_max_triangle_num_less_than(num, n)
    else:
        return n
    

class School(models.Model):
    
    def level(self):
        return get_max_triangle_num_less_than(self.rep / SCHOOL_REP_LEVEL_MODIFIER)
    
    name = models.CharField(max_length=64)
    # Rep could also be a DecimalField (needs max_digits and decimal_places specified)
    rep = models.IntegerField(default = 0)
    num_students = models.IntegerField(default = 0)
    
    def __init__(self, name, *args, **kwargs):
            models.Model.__init__(self, *args, **kwargs)
            self.name = name


class Student(models.Model):

    def level(self):
        return get_max_triangle_num_less_than(self.rep / STUDENT_REP_LEVEL_MODIFIER)
    
    user = models.ForeignKey(User, unique=True)
    school = models.ForeignKey(School)
    isHead = models.BooleanField()
    
    referral_code = models.CharField(max_length=128, unique=True)
    referred_by = models.ForeignKey(User, null=True, blank=True)
    
    rep = models.IntegerField(default = 0)

    def __init__(self, user, school, referred_by = None, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self.user = user
        self.school = school
        self.referred_by = referred_by
        
        # This automatically creates a custom string of letters/numbers -- I thought it was 
        #  the easiest way to make a custom "referral code" which can be used to link a 
        #  registration to the referrer
        self.referral_code = str(uuid.uuid4())

    
    
