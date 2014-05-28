from django.utils import unittest
from spudmart.CERN.models import School, Student#, STATES
from django.contrib.auth.models import User
from django.test import TestCase
import random

class StudentTest(TestCase):
    def setUp(self):
        self.school1 = School(state = "AK", name = "A Fine University")
        self.school2 = School(state = "OH", name = "The Finest University")
        self.school1.save()
        self.school2.save()
        
        self.user1 = User(username = "user1")
        self.user2 = User(username = "user2")
        self.user3 = User(username = "user3")
        self.user1.save()
        self.user2.save()
        self.user3.save()
        
        self.student1 = Student(user = self.user1, school = self.school1)
        self.student2 = Student(user = self.user2, school = self.school1, referred_by = self.user1)
        self.student3 = Student(user = self.user3, school = self.school2)
        self.student1.save()
        self.student2.save()
        self.student3.save()
        
        unittest.TestCase.setUp(self)

    def test_students_link_to_schools(self):
        self.assertEqual(self.school1, self.student1.school)
        self.assertEqual(self.school2, self.student3.school, "Student.school does not correctly point to school")
        
    def test_referrer_rep_link(self):
        old_rep = self.student1.rep
        points = random.randint(0, 100)
        self.student2.add_rep(points)
        rep_change = self.student1.rep - old_rep
        print rep_change
        self.assertEqual(rep_change, points, "Referrer does not get correct points added when referree gains points.")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSchool']
    unittest.main()