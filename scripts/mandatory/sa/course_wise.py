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








mandatory_courses = SKillOffering.objects.filter(is_mandatory=1)
for x in mandatory_courses:
    allocation_count = 0
    sub_count = 0
    export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/sa/'+x.course_name+'.csv'), 'w')
    writer = csv.writer(export_file)
    headers = ['college code', 'college name', 'branch','sem','invitation_id', 'roll_no','student_name', 'course_name', 'kp_name','enrollment_status','subscription_status']
    writer.writerow(headers)
    file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/sa/z170.csv'))
    csv_data = csv.reader(file)
    for record in csv_data:
        college_code = record[0]
        try:
            college_info = College.objects.get(college_code=college_code)
            mandatory_branches = MandatoryCourse.objects.filter(college_id=college_info.id,skill_offering_id=x.id).distinct('branch_id')
            mandatory_sems = list(mandatory_branches.distinct('sem').values('sem'))
            for branch in mandatory_branches:
                for sem in mandatory_sems:
                    b_s_students = Student.objects.filter(sem=sem['sem'],rbranch_id=branch.branch.id,college_id=college_info.id)
                    print(x.course_name,college_code,branch.branch.name,sem['sem'],b_s_students.count)
                    for student in b_s_students:
                        is_enrolled = None
                        try:
                            check_sf_e = SKillOfferingEnrollment.objects.get(student_id=student.id,is_mandatory=1,skill_offering_id=x.id)
                            is_enrolled = True
                            allocation_count = allocation_count + 1
                            is_subscribed = None
                            try:
                                subscription = StudentCourse.objects.get(student_id=student.id,course_id=check_sf_e.skill_offering.lms_course_id,status=1)
                                if subscription:
                                    is_subscribed = True
                                    sub_count = sub_count + 1
                                    data = [college_info.college_code, college_info.college_name, student.rbranch.name, student.sem, student.invitation_id, student.roll_no, student.aadhar_number, check_sf_e.skill_offering.course_name, check_sf_e.knowledge_partner.name,is_enrolled,is_subscribed]
                                    writer.writerow(data)
                            except StudentCourse.DoesNotExist:
                                is_subscribed = False
                                data = [college_info.college_code, college_info.college_name, student.rbranch.name, student.sem, student.invitation_id, student.roll_no, student.aadhar_number, check_sf_e.skill_offering.course_name, check_sf_e.knowledge_partner.name,is_enrolled,is_subscribed]
                                writer.writerow(data)
                            except MultipleObjectsReturned:
                                is_subscribed = True
                                sub_count = sub_count + 1
                                subscriptions = StudentCourse.objects.filter(student_id=student.id,course_id=check_sf_e.skill_offering.lms_course_id,status=1)
                                dup_sub = dup_sub + subscriptions.count()
                                data = [college_info.college_code, college_info.college_name, student.rbranch.name, student.sem, student.invitation_id, student.roll_no, student.aadhar_number, check_sf_e.skill_offering.course_name, check_sf_e.knowledge_partner.name,is_enrolled,is_subscribed]
                                writer.writerow(data)
                        except SKillOfferingEnrollment.DoesNotExist:
                            is_enrolled = False
                            data = [college_info.college_code, college_info.college_name, student.rbranch.name, student.sem, student.invitation_id, student.roll_no, student.aadhar_number, x.course_name, x.knowledge_partner.name,is_enrolled,False]
                            writer.writerow(data)
        except College.DoesNotExist:
            print("college missed----------------------------------------")
    print(x.course_name,allocation_count,sub_count,sep=',')