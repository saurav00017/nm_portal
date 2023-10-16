import csv
import os
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollment,SKillOfferingEnrollmentProgress, SKillOffering, MandatoryCourse

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/L&T/students.csv'))
csv_data = csv.reader(file)
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/L&T/students_data.csv'), 'w')
writer = csv.writer(export_file)

writer.writerow(next(csv_data) + [
    'Student',
    'total_score',
    'assessment status'
])

for record in csv_data:
    # kp_name,course,total_score,student_id,
    student_id = record[1]
    student = Student.objects.get(invitation_id=student_id)

    progress = SKillOfferingEnrollmentProgress.objects.filter(
        skill_offering_enrollment__student_id=student.id
    ).order_by('-created').first()
    if progress:
        record += [student.aadhar_number, progress.progress_percentage, progress.assessment_status]
    writer.writerow(record)