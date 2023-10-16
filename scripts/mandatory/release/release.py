import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollment, SKillOffering, MandatoryCourse

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/release/372.csv'))
csv_data = csv.reader(file)
count = 0
for record in csv_data:
    college_code = record[0]
    try:
        college_info = College.objects.get(college_code=college_code)
        college_info.mandatory_release = True
        college_info.course_allocation = 1
        college_info.save()
        count = count + 1
    except College.DoesNotExist:
        print(college_code)
        print("college missed----------------------------------------")

print("total released ", College.objects.filter(mandatory_release=True,course_allocation=1).count())
