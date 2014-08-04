from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from spudmart.CERN.models import School
import csv
from django.conf import settings
import os


def import_schools():
    # First, remove all existing schools:
    School.objects.all().delete()
    
    path_to_file = os.path.join(settings.PROJECT_ROOT, 'spudmart', 'CERN', 'schools.csv')

    with open(path_to_file, 'rb') as csvfile:
        schools = csv.reader(csvfile, delimiter='|')
        x = 0
        for school in schools:
            if x > 1:
                break
            x += 1
            try:
                school_obj = School(name=school[0], state=school[1])
                school_obj.save()
            except Exception as e:
                print school
                raise e


def strip_invalid_chars(messy_string):
    stripped_string = messy_string.replace(' ', '').replace('&', '')
    return stripped_string.replace('-', '').replace(',', '')


def add_school_address():
    path_to_file = os.path.join(settings.PROJECT_ROOT, 'spudmart', 'CERN', 'schools_with_addresses.csv')

    with open(path_to_file, 'rb') as csvfile:
        schools = csv.reader(csvfile)
        x = 0
        for school in schools:
            try:
                school_obj = School.objects.get(name=school[0], state=school[3])
                if not school_obj.full_address:
                    school_obj.full_address = school[1]
                    school_obj.save()
            except ObjectDoesNotExist:
                # sch = School(name=school[0], state=school[3], full_address=school[1])
                # sch.save()
                pass
            except MultipleObjectsReturned:
                sch1 = School.objects.filter(name=school[0], state=school[3])[0]
                sch1.full_address = school[1]
                sch1.save()
                for s in School.objects.filter(name=school[0], state=school[3], full_address=None):
                    s.delete()
            except Exception as e:
                print school
                raise e