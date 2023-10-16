
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

"""
        2220_Smart_Energy_Grid
        2219_EV_charging_system
        2218_Electric_Vehicle
"""

courses = [
    {
        'sk_code' : 2220,
        'file_name' : '2220_Smart_Energy_Grid' 
    },
        {
        'sk_code' : 2219,
        'file_name' : '2219_EV_charging_system' 
    },
        {
        'sk_code' : 2218,
        'file_name' : '2218_Electric_Vehicle' 
    }
]

for z in courses:
    file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/by_college_code/cousera/372.csv'))
    csv_data = csv.reader(file)

    export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/by_college_code/cousera/'+z['file_name']+'.csv'), 'w')
    writer = csv.writer(export_file)
    headers = ['Full Name','Email','External Id']
    writer.writerow(headers)

    for record in csv_data:
        college_code = record[0]
        try:
            college_info = College.objects.get(college_code=college_code)
            sk_code = z['sk_code']
            enrolments = SKillOfferingEnrollment.objects.filter(
                college_id = college_info.id,
                skill_offering_id=sk_code,
                is_mandatory=1,
            )
            print(sk_code,college_code,enrolments.count(),sep=',' )

            for x in enrolments:
                if x.student is not None:
                    data = [x.student.aadhar_number,x.student.email,x.student.invitation_id]
                    writer.writerow(data)
                elif x.student == None:
                    x.delete()
        except College.DoesNotExist:
            print("college missed----------------------------------------")