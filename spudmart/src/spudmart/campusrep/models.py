from django.contrib.auth.models import User
from django.db import models
import uuid

# 100 points to get from level 1 to 2 for venues
VENUE_REP_LEVEL_MODIFIER = 100
# 1000 points to get from level 1 to 2 for students/groundskeepers (10x venue requirement)
STUDENT_REP_LEVEL_MODIFIER = 1000
# 100000 points to get from level 1 to 2 for schools (10x student requirement)
SCHOOL_REP_LEVEL_MODIFIER = 100000


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
    ''' A model for School objects that stores a string literal of the school name, the 
        reputation level, and the number of students at the school.
        Includes method which evaluates level based on reputation 
    ''' 
    name = models.CharField(max_length=64)
    rep = models.IntegerField(default = 0)
    num_students = models.IntegerField(default = 0)
    
    def level(self):
        return get_max_triangle_num_less_than(self.rep / SCHOOL_REP_LEVEL_MODIFIER)

    def __str__(self, *args, **kwargs):
        return self.name + ", " + str(self.num_students) + " students, " + str(self.rep) + " rep"
    
    def __eq__(self, other):
        return self.pk == other.pk

    def save(self, force_insert=False, force_update=False, using=None):
        for student in Student.objects.filter(school = self):
            student.school = self
        return models.Model.save(self, force_insert, force_update, using)


class Student(models.Model):
    ''' A model for Student objects (Groundskeepers), which stores the standard Django 
        User object associated with the student, the school, whether the student is the
        Head Student, referral information, and the student's reputation.
    '''    
    user = models.ForeignKey(User, primary_key = True)
    school = models.ForeignKey(School)
    isHead = models.BooleanField()
    
    referral_code = models.CharField(max_length=128, unique=True)
    referred_by = models.ForeignKey(User, blank=True, null=True)
    
    rep = models.IntegerField(default = 0)

    def save(self, force_insert=False, force_update=False, using=None):
        ''' Default save method overwritten so that the School's student count is always
            accurate, and the student's referral_code is only assigned once.
        '''
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
        something += str(self.school.name) + ", " + str(self.rep) + " rep points"
        return something

    def delete(self, using=None):
        ''' Default delete method overwritten so that deleting a student updates the
            school's count to reflect the loss of a student.
        '''
        self.school.num_students -= 1
        return models.Model.delete(self, using)

    def __eq__(self, other):
        return self.user == other.user
