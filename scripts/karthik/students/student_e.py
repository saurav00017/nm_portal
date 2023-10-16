from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
import os
from django.conf import settings
from lms.models import StudentCourse
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment
import collections
from lms.models import LMSDevNames, LmsApiLog

college_codes = ["4114","3114"]

header = ['student', 'student_name','sem',  'courses_id', 'course', 'kp', 'allocated', 'subscribed', 'accessed']


m_courses = SKillOffering.objects.filter(is_mandatory=1)

for c in m_courses:
    all_courses = StudentCourse.objects.filter(course_id=c.lms_course_id, student_id__isnull=False)
    courses_raw = []

    with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/students/data/' + c.course_name + '.csv'), 'w') as f:

        writer = csv.writer(f)
        writer.writerow(header)
        for a_c in all_courses:
            api_log = LmsApiLog.objects.filter(
                lms_client_id=a_c.lms_client.id
            ).count()
            # courses_raw.append([
            #     a_c.student_id,
            #     a_c.student.aadhar_number,
            #     a_c.student.sem,
            #     c.id,
            #     c.course_name,
            #     c.knowledge_partner.name,
            #     'YES',
            #     'YES' if a_c.status == 1 else 'NO',
            #     'YES' if api_log.count() > 2 else 'NO',
            # ])
            writer.writerow([
                a_c.student_id,
                a_c.student.aadhar_number,
                a_c.student.sem,
                c.id,
                c.course_name,
                c.knowledge_partner.name,
                'YES',
                'YES' if a_c.status == 1 else 'NO',
                'YES' if api_log > 4 else 'NO',
            ])

