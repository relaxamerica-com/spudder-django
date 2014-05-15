from django.contrib.auth import User
from django.db import models
import uuid


class Student(models.Model):
	user = models.ForeignKey(User, unique=True)
	school = models.ForeignKey(School)
	# Rep could also be a DecimalField (needs max_digits and decimal_places specified)
	rep = models.IntegerField(default = 0)
	level = models.IntegerField(default = 1)
	referral_code = models.CharField(max_length=128, unique=True, default=uuid.uuid4)
	isHead = BooleanField()


class School(models.Model):
	name = models.CharField(max_length=64)
	# Rep could also be a DecimalField (needs max_digits and decimal_places specified)
	rep = models.IntegerField(default = 0)
	level = models.IntegerField(default = 1)
	num_students = models.IntegerField(default = 0)
	head_student = models.ForeignKey(Student)
