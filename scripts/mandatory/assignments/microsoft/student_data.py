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
                         'scripts/mandatory/assignments/microsoft/ms_2_output.csv'), 'w')
writer = csv.writer(file)
writer.writerow([
    'Phone number',
    'Phone number',
    None,
    None,
    None,
    None,
    None,
    None,
    'Student count',
    'verified',
    'student id',
    'Name',
    'email',
    'sem'
    'college code',
    'college',
    'course name',
    'internal_assessment_score',
    'ea_1',
    'ea_2',
    'ea_3',
])

with open(os.path.join(settings.BASE_DIR,
                       'scripts/mandatory/assignments/microsoft/MS_2.csv'), 'r') as f:
    csv_data = csv.reader(f)

    for record in csv_data:
        phone_number = record[0]

        students_list = Student.objects.filter(phone_number=phone_number)

        student_count = students_list.count()
        if students_list:
            for student in students_list:
                enrollment = SKillOfferingEnrollment.objects.filter(
                    is_mandatory=True,
                    student_id=student.id
                ).order_by('-created').first()
                if enrollment:
                    progress = SKillOfferingEnrollmentProgress.objects.filter(
                        skill_offering_enrollment_id=enrollment.id
                    ).order_by('-created').first()
                    if progress:
                        writer.writerow(record + [
                            student_count,
                            student.verification_status,
                            student.invitation_id,
                            student.aadhar_number,
                            student.email,
                            student.sem,
                            student.college.college_code if student.college_id else None,
                            student.college.college_name if student.college_id else None,
                            enrollment.skill_offering.course_name,
                            progress.progress_percentage,
                            progress.ea_1,
                            progress.ea_2,
                            progress.ea_3,
                        ])
                    else:
                        writer.writerow(record + [
                            student_count,
                            student.verification_status,
                            student.invitation_id,
                            student.aadhar_number,
                            student.email,
                            student.sem,
                            student.college.college_code if student.college_id else None,
                            student.college.college_name if student.college_id else None,
                            enrollment.skill_offering.course_name,

                        ])
                else:

                    writer.writerow(record + [
                        student_count,
                        student.verification_status,
                        student.invitation_id,
                        student.aadhar_number,
                        student.email,
                        student.sem,
                        student.college.college_code if student.college_id else None,
                        student.college.college_name if student.college_id else None,


                    ])

        else:

            writer.writerow(record + ['0'])