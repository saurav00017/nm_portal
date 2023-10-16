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

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/L&T/IDs_not_found-Table_1.csv'))
csv_data = csv.reader(file)
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/L&T/output_IDs_not_found-Table_1.csv'), 'w')
writer = csv.writer(export_file)


writer.writerow(next(csv_data) + [
    'name', 'email', 'college code', 'college',
    'kp_name', 'course name', 'ea_1', 'ea_2', 'ea_3', 'total_score'
    'kp_name', 'course name', 'ea_1', 'ea_2', 'ea_3', 'total_score'
])

for record in csv_data:
    # kp_name,course,total_score,student_id,
    student_id = record[3]
    student = Student.objects.get(invitation_id=student_id)

    record += [student.aadhar_number,
               student.email,
               student.college.college_code,
               student.college.college_name]

    enrollment = SKillOfferingEnrollment.objects.filter(
        is_mandatory=1,
        student_id=student.id
    ).order_by('-created').first()
    if enrollment:

        progress = SKillOfferingEnrollmentProgress.objects.filter(
            skill_offering_enrollment_id=enrollment.id
        ).order_by('-created').first()
        if progress:
            record += [
                enrollment.skill_offering.knowledge_partner.name,
                enrollment.skill_offering.course_name,
                progress.ea_1,
                progress.ea_2,
                progress.ea_3,
                progress.progress_percentage,
            ]
    writer.writerow(record)
