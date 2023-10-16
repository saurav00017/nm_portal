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

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/L&T/l&t_assessment_clear.csv'))
csv_data = csv.reader(file)
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/L&T/output_l&t_assessment_clear.csv'), 'w')
writer = csv.writer(export_file)

writer.writerow([
    'course', 'student_id', None, 'name', 'status', 'exception'
])

for record in csv_data:
    course = record[0]
    student_id = record[1]
    try:
        student = Student.objects.get(invitation_id=student_id)
        enrollment = SKillOfferingEnrollment.objects.filter(
            skill_offering__knowledge_partner_id=77,
            student_id=student.id
        ).order_by('-created').first()
        if enrollment:
            progress = SKillOfferingEnrollmentProgress.objects.filter(
                skill_offering_enrollment_id=enrollment.id
            ).order_by('-created').first()
            progress.assessment_data = None
            progress.save()
            record = [
                enrollment.skill_offering.course_name,
                student_id, progress.progress_percentage,
                student.aadhar_number, 'done']
        else:
            record = [None, None, None, None, None, "No subscription"]

    except Student.DoesNotExist:
        record = [None, None, None, None, None, "Student not found"]

    writer.writerow(record)