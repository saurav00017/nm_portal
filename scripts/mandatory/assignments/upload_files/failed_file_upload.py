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
                         'scripts/mandatory/assignments/upload_files/infosys_failed_data_while_upload.csv'), 'w')
writer = csv.writer(file)

for record in CourseBulkUpload.objects.filter(course_type=2, created__date='2022-12-12'):
    data = record.result_data
    if data:
        exception_student_data = data['exception_student_data']
        student_not_found_data = data['student_not_found_data']
        student_more_than_one_data = data['student_more_than_one_data']
        enrollment_not_found_data = data['enrollment_not_found_data']
        if 'exception_student_data' in data:
            for email in data['exception_student_data']:
                writer.writerow([
                    email,
                    'Exception'
                ])
        if 'student_not_found_data' in data:
            for email in data['student_not_found_data']:
                writer.writerow([
                    email,
                    'Student not found'
                ])
        if 'student_more_than_one_data' in data:
            for email in data['student_more_than_one_data']:
                writer.writerow([
                    email,
                    'More then one student exist'
                ])
        if 'enrollment_not_found_data' in data:
            for email in data['enrollment_not_found_data']:
                writer.writerow([
                    email,
                    'Course not subscribed'
                ])