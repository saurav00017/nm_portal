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

data = {
    "failed_student_count": 6152,
    "success_student_count": 81324,
    "student_not_found_data": [{"phone_number": "7406638642"}],
    "enrollment_not_found_count": 0}
file = open(os.path.join(settings.BASE_DIR,
                         'scripts/mandatory/assignments/upload_files/microsoft_failed_data_while_upload.csv'), 'w')
writer = csv.writer(file)
writer.writerow([
    'Course',
    'Phone number',
    'Reason'
])

for record in CourseBulkUpload.objects.filter(course_type=1, created__date='2022-12-12'):
    course_name = record.skill_offering.course_name
    data = record.result_data
    if data:
        if 'student_not_found_data' in data:
            for student in data['student_not_found_data']:
                writer.writerow([
                    course_name,
                    student['phone_number'],
                    'Student not found'
                ])

