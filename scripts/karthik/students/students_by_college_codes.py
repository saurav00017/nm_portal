from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
import os
from django.conf import settings
from lms.models import StudentCourse
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment
import collections
from student.models import Student

college_codes = ["7179","2127","1116","7277","8104","3106","7113","7276","7140","9207","7304","9204","8115","1119","3109","7217","9522","6123","1118","1115"]

header = ['student_id', 'student_name', 'sem',  'branch', 'roll_number', 'phone_number', 'email']


m_courses = SKillOffering.objects.filter(is_mandatory=1)

print(len(college_codes))
for c in college_codes:
    with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/students/data/' + c + '.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        students = Student.objects.filter(college__college_code=c)
        for student in students:
            writer.writerow([
                student.id,
                student.aadhar_number,
                student.sem,
                student.rbranch_id,
                student.roll_no,
                student.phone_number,
                student.email,
            ])

