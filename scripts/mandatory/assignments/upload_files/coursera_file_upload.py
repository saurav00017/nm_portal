import json
import os
import csv
from django.conf import settings
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import CourseBulkUpload

file = open(os.path.join(settings.BASE_DIR,
                         'scripts/mandatory/assignments/upload_files/coursera_failed_data_while_upload.csv'), 'w')
writer = csv.writer(file)
writer.writerow([
    'Course',
    'Email',
    'Reason'
])

for record in CourseBulkUpload.objects.filter(course_type=0, created__date='2022-12-12'):
    course_name = record.skill_offering.course_name
    data = record.result_data
    if data:
        if 'invalid_student_ids' in data:
            for student_id in data['invalid_student_ids']:
                writer.writerow([
                    course_name,
                    student_id,
                    'Student not found'
                ])

        if 'invalid_enrollment' in data:
            for student_id in data['invalid_enrollment']:
                writer.writerow([
                    course_name,
                    student_id,
                    'Course not subscribed'
                ])
