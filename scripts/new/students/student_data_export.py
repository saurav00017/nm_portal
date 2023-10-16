from student.models import Student
from college.models import College
from django.db.models import F
from datarepo.models import CollegeType
import os
import os
from django.conf import settings
from kp.models import KnowledgePartner
from skillofferings.models import SKillOfferingEnrollment, SKillOffering
from lms.models import LMSClient, Course, CourseStatus, StudentCourse, RecordType, CourseHistory

read_file_name = "scripts/new/students/TCS Students - Annexure IV List of selected students from DoTE colleges - DOTE.csv"
write_file_name = "scripts/new/students/export_TCS Students - Annexure IV List of selected students from DoTE colleges - DOTE.csv"

"""
0 1383,
1 NQT22051224686,
2 Mahendran,
3 M,
4 mahendranofficial2002@gmail.com,
5 8489387163,
6 "University College of Engineering, BIT Campus",
7 6th,
8 General,Machine learning for real-world application,DOTE,810019102025
"""

import csv
with open(write_file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    with open(os.path.join(settings.BASE_DIR, read_file_name), 'r') as file:
        csv_data = csv.reader(file)
        index = 0
        for record in csv_data:
            if index!=0:
                roll_no = record[-1]
                try:
                    get_student = Student.objects.get(roll_no__iexact=roll_no, college_id__isnull=False)
                    record += [
                        True,
                        get_student.email,
                        get_student.invitation_id
                    ]

                except Student.MultipleObjectsReturned:
                    try:
                        get_student = Student.objects.get(roll_no__iexact=roll_no, college_id__isnull=False)
                        record += [
                            True,
                            get_student.email,
                            get_student.invitation_id,
                        ]
                    except  Student.MultipleObjectsReturned:
                        students = Student.objects.values('id').filter(roll_no__iexact=roll_no, college_id__isnull=False)
                        record += ['','','','','',students.count(), list(students.values('id', 'college_id',"aadhar_number"))]
                except Student.DoesNotExist:
                    record += [
                        False,
                        "",
                        ""
                    ]
                except Exception as e:
                    print("Error at - ", e)
                course_name = str(record[9])
                print(course_name)

                try:
                    get_course = Course.objects.get(lms_client_id=1, course_name__iexact=course_name)
                    check_student_subscription = StudentCourse.objects.filter(
                        course_id=get_course.id,
                        student_id=get_student.id).first()
                    if not check_student_subscription:
                        new_subscription = StudentCourse.objects.create(
                            student_id=get_student.id,
                            course_id=get_course.id,
                            lms_client_id=get_course.lms_client_id,
                        )
                        record += ["Student Course-", str(new_subscription.id)]
                    else:
                        record += ["Student Course-", str(check_student_subscription.id)]
                    try:
                        get_skill_offering = SKillOffering.objects.filter(lms_course_id=get_course.id).first()
                    except:
                        get_skill_offering = None
                    offering_type = None
                    if get_course.course_type == "ONLINE":
                        offering_type = 1
                    else:
                        offering_type = 0
                    get_knowledge_partner = KnowledgePartner.objects.get(lms_client_id=get_course.lms_client_id)

                    get_skill_offering_enrollment = SKillOfferingEnrollment.objects.filter(
                        student_id=get_student.id,
                        knowledge_partner_id=get_knowledge_partner.id if get_knowledge_partner else None,
                        skill_offering_id=get_skill_offering.id if get_skill_offering else None,
                    ).first()

                    if not get_skill_offering_enrollment:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                            student_id=get_student.id,
                            college_id=get_student.college_id,
                            lms_course_id=get_course.id,
                            skill_offering_id=get_skill_offering.id if get_skill_offering else None,
                            # vendor=get_knowledge_partner.name if get_knowledge_partner else None,
                            knowledge_partner_id=get_knowledge_partner.id if get_knowledge_partner else None,
                            status=4,  # Approved Directly by KP
                            offering_type=offering_type,
                        )
                        record += ["Skill Entrolement "+ str(new_skill_offering_enrollment.id)]
                    else:
                        record += ["Skill Entrolement "+ str(get_skill_offering_enrollment.id)]
                        print("get_skill_offering_enrollment", get_skill_offering_enrollment)
                except Course.DoesNotExist:
                    record += ["No Course"]
            writer.writerow(record)
            index += 1

            print("Counter -- ", index)