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
from lms.models import StudentCourse
import time

"""
1. From zone one college codes
2. Get Mandatory branches
3. Get SEMs
4. Get courses
5. allocation count
6. subscribe count
"""

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/sa/z170.csv'))
csv_data = csv.reader(file)

export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/sa/raw.csv'), 'w')
writer = csv.writer(export_file)

headers = ['college code', 'college name', 'branch','sem','invitation_id', 'roll_no','student_name', 'course_name', 'kp_name']
writer.writerow(headers)

total_zone_1_allocations = 0
enrollment_count = 0
sub_count = 0
dup_sub = 0
for record in csv_data:
    college_code = record[0]
    try:
        college_info = College.objects.get(college_code=college_code)
        mandatory_branches = MandatoryCourse.objects.filter(college_id=college_info.id).distinct('branch_id')
        mandatory_sems = list(mandatory_branches.distinct('sem').values('sem'))
        for branch in mandatory_branches:
            for sem in mandatory_sems:
                print(branch.id,sem['sem'])
                b_s_students = Student.objects.filter(sem=sem['sem'],rbranch_id=branch.branch.id,college_id=college_info.id)
                for student in b_s_students:
                    try:
                        check_sf_e = SKillOfferingEnrollment.objects.get(student_id=student.id,is_mandatory=1)
                        enrollment_count = enrollment_count + 1
                        try:
                            subscription = StudentCourse.objects.get(student_id=student.id,course_id=check_sf_e.skill_offering.lms_course_id,status=1)
                            if subscription:
                                sub_count = sub_count + 1
                                data = [college_info.college_code, college_info.college_name, student.rbranch.name, student.sem, student.invitation_id, student.roll_no, student.aadhar_number, check_sf_e.skill_offering.course_name, check_sf_e.knowledge_partner.name]
                                writer.writerow(data)
                        except StudentCourse.DoesNotExist:
                            pass
                        except MultipleObjectsReturned:
                            sub_count = sub_count + 1
                            subscriptions = StudentCourse.objects.filter(student_id=student.id,course_id=check_sf_e.skill_offering.lms_course_id,status=1)
                            dup_sub = dup_sub + subscriptions.count()
                            data = [college_info.college_code, college_info.college_name, student.rbranch.name, student.sem, student.invitation_id, student.roll_no, student.aadhar_number, check_sf_e.skill_offering.course_name, check_sf_e.knowledge_partner.name]
                        print(sub_count)
                        print(dup_sub)
                    except SKillOfferingEnrollment.DoesNotExist:
                        pass
    except College.DoesNotExist:
        print("college missed----------------------------------------")
print(total_zone_1_allocations)
print(enrollment_count)
print(sub_count)