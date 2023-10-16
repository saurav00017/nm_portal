from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
import os
from django.conf import settings
from lms.models import StudentCourse
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment
import collections
from lms.models import LMSDevNames, LmsApiLog

zone1CollegeCodes = ["4114","3114","3116","4107","4103","4115","4117","4120","1114","4","3107","1101","1126","1127","3115","2126","4106","2119","2115","2124","2128","1106","1103","1138","2104","2102","2111","2113","1120","2101","1128","2109","3103","3101","2120","4101","1125","4108","2106","3108","2129","4121","4116","1133","4123","3111","2","1111","3121","3118","4127","3128","2105","3105","5134","2117","1","2108","4130","3126","2112","1107","3110","1108","4126","1105","1123","1124","3125","4118"]


all_mc = SKillOffering.objects.filter(is_mandatory=1)

header1 = ['course_name', 'allocated', 'subscribed']

header = ['student', 'unique id', 'roll no', 'student_name','sem', 'college_code', 'college_name'  'courses_id', 'course', 'kp', 'allocated', 'subscribed']

cFile = open(os.path.join(settings.BASE_DIR, 'scripts/karthik/students/data/all_c.csv'), 'w')
writer1 = csv.writer(cFile)
writer1.writerow(header1)

for mc in all_mc:

    with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/students/data/' + mc.course_name + '.csv'), 'w') as f:

        writer = csv.writer(f)
        writer.writerow(header)

        all_students = SKillOfferingEnrollment.objects.filter(skill_offering_id=mc.id, student_id__isnull=False).exclude(student_id=None).distinct('student_id')
        all_students_count = all_students.count()
        student_ids = []
        for student in all_students:
            try:
                student_ids.append(student.student_id)

                sc = StudentCourse.objects.filter(student_id=student.student_id, course_id=mc.lms_course_id).count()
                writer.writerow([
                    student.student_id,
                    student.student.invitation_id,
                    student.student.roll_no,
                    student.student.aadhar_number,
                    student.student.sem,
                    student.college.college_code,
                    student.college.college_name,
                    mc.id,
                    mc.course_name,
                    mc.knowledge_partner.name,
                    'YES',
                    'YES' if sc >= 1 else 'NO',
                ])
            except:
                print(student.student_id)

        all_student_courses = StudentCourse.objects.filter(student_id__in=student_ids, course_id=mc.lms_course_id, student_id__isnull=False).distinct('student_id')
        
        print(mc.id, mc.course_name, all_students_count, all_student_courses.count())
        writer1.writerow([mc.course_name, all_students_count, all_student_courses.count()])