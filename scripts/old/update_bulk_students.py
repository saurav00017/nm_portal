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


with open(os.path.join(settings.BASE_DIR, 'scripts/student_branch_data.csv')) as file:
    csv_data = csv.reader(file)
    old_college_code = None
    college_id = None
    for record in csv_data[0:10]:
        try:
            roll_no = record[3]
            specialization = record[2]
            try:
                get_student = Student.objects.get(
                    roll_no=roll_no
                )
                if get_student:
                    get_student.specialization=specialization
                    bulk_students.append(get_student)
            except:
                pass
        except Exception as e:
            print(e)
            failed_data.append(record)
    file.close()
print(len(bulk_students))
print(Student.objects.bulk_update(bulk_students, 'specialization'))
print(failed_data)
