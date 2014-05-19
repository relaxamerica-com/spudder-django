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

    def __str__(self, *args, **kwargs):
        return self.name + ", " + str(self.num_students) + " students, " + str(self.rep) + " rep"
    
    def get_name(self):
        return str(self.name)

class Student(models.Model):

    def level(self):
        return get_max_triangle_num_less_than(self.rep / STUDENT_REP_LEVEL_MODIFIER)
    
    user = models.ForeignKey(User, unique=True)
    school = models.ForeignKey(School)
    isHead = models.BooleanField()
    
    referral_code = models.CharField(max_length=128, unique=True)
    referred_by = models.ForeignKey(User, blank=True, null=True)
    
    rep = models.IntegerField(default = 0)

    def save(self, force_insert=False, force_update=False, using=None):
        if self.pk is None:
            self.school.num_students += 1
            self.referral_code = str(uuid.uuid4())
        return models.Model.save(self, force_insert, force_update, using)


    def __str__(self):
        something = str(self.user.username)
        if self.isHead:
            something += ", Head at "
        else:
            something += ", at "
        something += str(self.school.get_name()) + ", " + str(self.rep) + " rep points"
        return something


    
    
