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

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/coursera/Coursera-Sheet1.csv'))
csv_data = csv.reader(file)
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/coursera/data.csv'), 'w')
writer = csv.writer(export_file)


writer.writerow(['', '', 'student_id', '','',
                 'ea_1', 'ea_2', 'ea_3', 'total_score', 'assessment status', 'course_complete'
])

for record in csv_data:
    # kp_name,course,total_score,student_id,
    student_id = record[2]
    student = Student.objects.get(invitation_id=student_id)

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
                progress.ea_1,
                progress.ea_2,
                progress.ea_3,
                progress.progress_percentage,
                progress.assessment_status,
                progress.course_complete,
            ]
    writer.writerow(record)
