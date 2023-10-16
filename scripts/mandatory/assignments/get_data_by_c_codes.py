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

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/370.csv'))
csv_data = csv.reader(file)
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/msofficedata.csv'), 'w')
writer = csv.writer(export_file)
headers = ['college_code', 'college_name', 'student_name', 'student_email', 'student_phone', 'branch_id', 'branch_name']
writer.writerow(headers)
count = 0
for record in csv_data:
    college_code = record[0]
    try:
        college_info = College.objects.get(college_code=college_code)
        # students_list
        students_list = Student.objects.filter(college=college_info, sem=3)
        for x in students_list:
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
            data = [x.college.college_code, x.college.college_name, x.aadhar_number,
                    x.email, x.phone_number, x.rbranch.id if x.rbranch is not None else None, x.rbranch.name if x.rbranch is not None else None]
            writer.writerow(data)
            count = count + 1
            print(x.college.college_code,students_list.count(),count,students_list.count() - count,sep=' | ')
    except College.DoesNotExist:
        print("college missed----------------------------------------")


"""
        SKillOfferingEnrollment.objects.filter(skill_offering_id=2227).count()SKillOfferingEnrollment.objects.filter(skill_offering_id=2227).count()
"""