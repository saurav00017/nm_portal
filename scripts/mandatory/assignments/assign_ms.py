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

count = 0
file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/372.csv'))
csv_data = csv.reader(file)
for record in csv_data:
    college_code = record[0]
    try:
        college_info = College.objects.get(college_code=college_code)
        # students_list
        students_list = Student.objects.filter(college=college_info, sem=3)
        for x in students_list:
            try:
                new_mandatory_course = SKillOfferingEnrollment.objects.get(
                    student_id=x.id,
                    college_id=x.college.id,
                    knowledge_partner_id=76,
                    skill_offering_id=2227,
                    status=4,
                    offering_type=2,
                    offering_kind=0,
                    is_mandatory=1)
                new_mandatory_course.save()
            except SKillOfferingEnrollment.DoesNotExist:
                print(x.id)
                count = count + 1
                new_mandatory_course = SKillOfferingEnrollment.objects.create(
                    student_id=x.id,
                    college_id=x.college.id,
                    knowledge_partner_id=76,
                    skill_offering_id=2227,
                    status=4,
                    offering_type=2,
                    offering_kind=0,
                    is_mandatory=1)
                new_mandatory_course.save()
            print(x.college.college_code,count,sep=' | ')
    except College.DoesNotExist:
        print("college missed----------------------------------------")

