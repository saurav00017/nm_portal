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
                         'scripts/mandatory/assignments/microsoft/duplicate_phone_numbers.csv'), 'w')
writer = csv.writer(file)
writer.writerow([
    'Phone number',
    'Student_unique id',
    ' Roll number',
    'college code',
    'college name',
    'sem',
    'branch',
    'student name',
    'Internal assessment total score',
    'ea_1',
    'ea_2',
    'ea_3',
])

enrollments_list = SKillOfferingEnrollment.objects.filter(skill_offering__knowledge_partner_id=76)

student_phone_numbers =enrollments_list.distinct(
    'student__phone_number'
).values_list('student__phone_number', flat=True)
skill_offering_ids = enrollments_list.distinct(
    'skill_offering_id'
).values_list('skill_offering_id', flat=True)
total_count = len(student_phone_numbers)
for index, phone_number in enumerate(student_phone_numbers):
    print("Pending ---> ", total_count - index)

    student_list = enrollments_list.filter(
        skill_offering_id__in=skill_offering_ids,
        student__phone_number=phone_number
    ).distinct('student_id', 'skill_offering_id').values('student_id', 'skill_offering_id')

    for record in student_list:
        progress = SKillOfferingEnrollmentProgress.objects.select_related(
            'skill_offering_enrollment',
            'skill_offering_enrollment__skill_offering',
            'skill_offering_enrollment__student',
            'skill_offering_enrollment__student__college',
        ).filter(
            skill_offering_enrollment__student_id=record['student_id'],
            skill_offering_enrollment__skill_offering_id=record['skill_offering_id']
        ).order_by('-created').first()
        if progress:
            writer.writerow([
                progress.skill_offering_enrollment.student.phone_number,
                progress.skill_offering_enrollment.student.invitation_id,
                progress.skill_offering_enrollment.student.roll_no,
                progress.skill_offering_enrollment.student.college.college_code,
                progress.skill_offering_enrollment.student.college.college_name,
                progress.skill_offering_enrollment.student.sem,
                progress.skill_offering_enrollment.student.rbranch.name if progress.skill_offering_enrollment.student.rbranch_id else None,
                progress.skill_offering_enrollment.student.aadhar_number,
                progress.progress_percentage,
                progress.ea_1,
                progress.ea_2,
                progress.ea_3
            ])
        else:
            skill_offering_enrollment = enrollments_list.filter(
                student_id=record['student_id'],
                skill_offering_id=record['skill_offering_id']
            ).order_by('-created').first()
            if skill_offering_enrollment:
                writer.writerow([
                    skill_offering_enrollment.student.phone_number,
                    skill_offering_enrollment.student.invitation_id,
                    skill_offering_enrollment.student.roll_no,
                    skill_offering_enrollment.student.college.college_code,
                    skill_offering_enrollment.student.college.college_name,
                    skill_offering_enrollment.student.sem,
                    skill_offering_enrollment.student.rbranch.name if skill_offering_enrollment.student.rbranch_id else None,
                    skill_offering_enrollment.student.aadhar_number
                ])



