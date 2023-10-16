from student.models import Student
from college.models import College
from users.models import User
import csv
import os.path
import os
from django.conf import settings
import time
import asyncio
from io import StringIO


with open(os.path.join(settings.BASE_DIR, 'scripts/students/students_aug25.tsv')) as file:
    csv_data = csv.reader(file, delimiter="\t")
    college_id = None
    for record in csv_data:
        try:
            college_code = record[0]
            roll_no = record[1]
            sem = int(str(record[2])) + 1
            phone_number = record[3]
            email = record[4]
            branch = record[5]
            try:
                student_info = Student.objects.get(
                    roll_no=roll_no,
                )
                student_info.sem = sem
                student_info.phone_number = phone_number
                student_info.email = email
                student_info.branch = branch
                student_info.save()
                updated = updated + 1
            except Student.DoesNotExist:
                not_updated = not_updated + 1
        except Exception as e:
            print(e)
            failed_data.append(record)
        print('updated ', updated)
        print('not updated ', not_updated)
    file.close()
