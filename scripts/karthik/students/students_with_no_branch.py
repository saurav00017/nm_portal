from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
import os
from django.conf import settings
from lms.models import StudentCourse
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment
import collections
from student.models import Student
from itertools import groupby
from operator import itemgetter

header = ['student_id', 'student_name', 'sem',  'branch', 'roll_number', 'phone_number', 'email']

m_courses = SKillOffering.objects.filter(is_mandatory=1)


colleges = Student.objects.filter(rbranch__isnull=True, sem=3, id__isnull=False, college_id__isnull=False).distinct('college_id')

for c in colleges:
    students = Student.objects.filter(rbranch__isnull=True, sem=3, college_id=c.college.id, id__isnull=False)
    print(c.college.college_code, colleges.count(), students.count())
    with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/students/data/no_branch_students_' + c.college.college_code + '.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
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

