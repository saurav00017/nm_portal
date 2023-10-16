
import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datarepo.models import Branch, CollegeType
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
import time
from skillofferings.models import SKillOfferingEnrollment, SKillOffering, MandatoryCourse

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/by_college_code/cousera/372.csv'))
csv_data = csv.reader(file)

code_index = 0
student_index = 0
start_time = time.time()
with open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/course_allocation/cambridge_allocation_list.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerow([
        'allocation_id',
        'student_id',
        'roll_no',
        'student name',
        'phone number',
        'email',
        'sem',
        'branch',
        'college_code',
        'college name',
    ])

    for record in csv_data:
        college_code = record[0]
        code_index += 1
        try:
            college_info = College.objects.values('id').get(college_code=college_code, college_type=CollegeType.ENGINEERING)
            students_list = Student.objects.filter(college_id=college_info['id'], sem=1)
            total_students_count = students_list.count()

            for index, student in enumerate(students_list):
                student_index += 1
                try:
                    enrollment = SKillOfferingEnrollment.objects.get(
                        student_id=student.id,
                        skill_offering_id=2215,
                    )
                except SKillOfferingEnrollment.DoesNotExist:
                    enrollment = SKillOfferingEnrollment.objects.create(
                        student_id=student.id,
                        college_id=college_info['id'],
                        skill_offering_id=2215,
                        lms_course_id=76,
                        knowledge_partner_id=103,
                        status=4,
                        offering_type=1,
                        offering_kind=1,
                        is_mandatory=1,
                    )
                writer.writerow([
                    # 'allocation_id',
                    enrollment.id,
                    # 'student_id',
                    student.invitation_id,
                    # 'roll_no',
                    student.roll_no,
                    # 'student name',
                    student.aadhar_number,
                    # 'phone number',
                    student.phone_number,
                    # 'email',
                    student.email,
                    # 'branch',
                    student.rbranch.name if student.rbranch else None,
                    # 'sem',
                    student.sem,
                    # 'college_code',
                    student.college.college_code,
                    # 'college name',
                    student.college.college_name
                ])
                end_time = time.time() - start_time
                print(f"{student_index} >>> {time.strftime('%H:%M:%S',time.gmtime(end_time))}  >>>>>> {code_index} - College Code({college_code}) | Pending ----> {total_students_count - index} / {total_students_count}")
        except College.DoesNotExist:
            print(f"{code_index} college missed----------------------------------------{college_code}")

