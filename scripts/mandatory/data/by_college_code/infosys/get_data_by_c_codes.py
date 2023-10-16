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
        2224_Machine Learning
        2223_Machine Learning with application to object recognition
        2222_Cyber Security
        2221_Full Stack
"""

courses = [
    {
        'sk_code' : 2224,
        'file_name' : '2224_Machine_Learning' 
    },
        {
        'sk_code' : 2223,
        'file_name' : '2223_Machine_Learning_object' 
    },
        {
        'sk_code' : 2222,
        'file_name' : '2222_Cyber_Security' 
    },
        {
        'sk_code' : 2221,
        'file_name' : '2221_Full_Stack' 
    },
]

for z in courses:
    file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/by_college_code/infosys/372.csv'))
    csv_data = csv.reader(file)

    export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/by_college_code/infosys/'+z['file_name']+'.csv'), 'w')
    writer = csv.writer(export_file)

    headers = ['First name', 'Last name', 'Email id', 'Phone number', 'Is minor (yes/NO)', 'Gender', 'Grade', 'Institution/University Code (AISHE CODE)']
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
            print(z,sk_code,college_code,enrolments.count(),sep=',' )

            for x in enrolments:
                if x.student is not None:
                    gender = 'Male' if x.student.gender == 1 else 'Female' if x.student.gender == 2 else 'Other' if x.student.gender == 3 else 'Do not wish to disclose'
                    _full_name = x.student.aadhar_number
                    full_name = str(_full_name).split(" ", 1)
                    first_name = None
                    last_name = None
                    if len(full_name) > 1:
                        first_name = full_name[0]
                        last_name = full_name[1]
                    else:
                        first_name = _full_name
                    data = [first_name,last_name, x.student.email, x.student.phone_number, "NO",gender, 'Graduate', "U-U-" + str(x.college.college_code).replace(" ", "")]
                    writer.writerow(data)
                elif x.student == None:
                    x.delete()
        except College.DoesNotExist:
            print("college missed----------------------------------------")