from spudmart.campusrep.models import School
import csv
from django.conf import settings
import os

def import_schools():
    path_to_file = os.path.join(settings.PROJECT_ROOT, 'spudmart', 'campusrep', 'schools.csv')
    with open(path_to_file, 'rb') as csvfile:
        schools = csv.reader(csvfile, delimiter = '|')
        
        for school in schools:
            try:
                school_obj = School(name = school[0], state = school[1])
                school_obj.save()
            except Exception as e:
                print school
                raise e