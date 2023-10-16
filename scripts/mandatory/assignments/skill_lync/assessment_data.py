import json
import os
import csv
from django.conf import settings
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollment, SKillOfferingEnrollmentProgress

file = open(os.path.join(settings.BASE_DIR,
                         'scripts/mandatory/assignments/skill_lync/assessment_data.csv'), 'w')
writer = csv.writer(file)
writer.writerow([
    'Course',
    'Email',
    'Reason'
])

enrollments_list = SKillOfferingEnrollment.objects.filter(
    is_mandatory=True,
    skill_offering__knowledge_partner_id=100,
    skill_offering_id__isnull=False,
    student_id__isnull=False,
).distinct('skill_offering_id', 'student_id').order_by('skill_offering_id').values('skill_offering_id', 'student_id')

progress_list = SKillOfferingEnrollmentProgress.objects.filter(
    skill_offering_enrollment__skill_offering__knowledge_partner_id=100,
    skill_offering_enrollment__is_mandatory=True,
)
total = enrollments_list.count()
for index, enrollment in enumerate(enrollments_list):
    print("Pending --> ", total - index)
    progress = progress_list.filter(
        skill_offering_enrollment__skill_offering_id=enrollment['skill_offering_id'],
        skill_offering_enrollment__student_id=enrollment['student_id'],
    ).order_by('-created').first()
    if progress:
        writer.writerow([
            progress.skill_offering_enrollment.skill_offering.course_name,
            progress.skill_offering_enrollment.student.invitation_id,
            progress.progress_percentage
        ])
    else:
        student = Student.objects.get(id=enrollment['student_id'])
        writer.writerow([
            None,
            student.invitation_id,
            None,
            'Progress not found'
        ])

