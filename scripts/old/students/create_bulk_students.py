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
from django.db.models import F
success_data = []
failed_data = []
bulk_students = []


with open(os.path.join(settings.BASE_DIR, 'scripts/students/student_final_25_08.csv')) as file:
    csv_data = csv.reader(file)
    old_college_code = None
    college_id = None
    index = 0
    for record in csv_data:
        try:
            college_code = record[0]
            branch = record[1]
            roll_no = record[2]
            student_name = record[3]
            sem = record[4]
            email = record[5]
            phone_number = record[6]
            if old_college_code != college_code:
                old_college_code = college_code
                try:
                    college = College.objects.values('id').get(college_code=college_code)
                    if college:
                        college_id = college['id']
                except Exception as e:
                    print(e)
                    college_id = None
            new_student = Student(
                roll_no=roll_no,
                college_id=college_id,
                registration_status=4,
                aadhar_number=student_name,
                branch=branch,
                email=email,
                phone_number=phone_number,
                hall_ticket_number=roll_no,
                sem=sem
            )
            bulk_students.append(new_student)
        except Exception as e:
            print(e)
            failed_data.append(record)
    file.close()
print("Started")
print(Student.objects.bulk_create(bulk_students))
print("Bulk Uploaded")
print("Updated Sem", Student.objects.update(sem=F('sem')+1))
print(Student.objects.count())
print(failed_data)
