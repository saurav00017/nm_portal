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


file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/zone2.csv'))
csv_data = csv.reader(file)

export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/zone2_Smart_energy_grid.csv'), 'w')
writer = csv.writer(export_file)

headers = ['Full Name','Email','External ID']
writer.writerow(headers)


for record in csv_data:
    college_code = record[0]

    try:
        college_info = College.objects.get(college_code=college_code)
        sk_code = 2220
        enrolments = SKillOfferingEnrollment.objects.filter(
            college_id = college_info.id,
            skill_offering_id=sk_code,
        )
        print(college_info.college_code,enrolments.count(),sep=',' )
        for x in enrolments:
            if x.student is not None:
                data = [x.student.aadhar_number,x.student.email,x.student.invitation_id]
                writer.writerow(data)
            elif x.student == None:
                x.delete()
    except College.DoesNotExist:
        print("Test")