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


success_data = []
failed_data = []
bulk_students = []


with open(os.path.join(settings.BASE_DIR, 'scripts/students/student_final_25_08.csv')) as file:
    csv_data = csv.reader(file)
    old_college_code = None
    for record in csv_data:
        try:
            college_code = record[0]
            roll_no = record[2]
            student_name = record[3]
            if old_college_code != college_code:
                old_college_code = college_code
                try:
                    college = College.objects.values('id').get(college_code=college_code)
                    if college:
                        college_id = college['id']
                except:
                    college_id = None
            college_code = record[0]
            roll_no = record[2]
            get_student = Student.objects.get(roll_no=roll_no)

        except Exception as e:
            print("Error", e)