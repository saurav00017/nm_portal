from student.models import Student
import csv
from college.models import College
import os.path
import os
from django.conf import settings
from datetime import datetime

"""
372622
"""
final_bulk_students = []
file_name = "scripts/oct3_eve.csv"
count = 0
fcount = 0
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    with open(os.path.join(settings.BASE_DIR, "scripts/oct3students.csv"), 'r') as file:
        csv_data = csv.reader(file)
        old_college_code = None
        college_id = None
        for record in csv_data:
            try:
                college_code = record[0]
                roll_no = record[1]
                name = record[2]
                branch_id = int(record[3])
                sem = None
                try:
                    sem = int(record[4])
                except:
                    sem = None
                if old_college_code != college_code:
                    old_college_code = college_code
                    try:
                        college = College.objects.values('id').get(college_code=str(college_code))
                        if college:
                            college_id = college['id']
                    except College.DoesNotExist:
                        print("College Code Does not exit: ", college_code)
                        college_id = None
                        writer.writerow(record)
                        fcount += 1
                if college_id:
                    new_student = Student(
                        payment_status=2,
                        registration_status=4,
                        roll_no=roll_no,
                        sem=sem,
                        rbranch_id=branch_id,
                        aadhar_number=name,
                        college_id=college_id,
                        degree=2,
                        phone_number=record[5],
                        email=record[6],
                    )
                    final_bulk_students.append(new_student)
                    count = count + 1

            except Exception as e:
                print("Error", e)
            print("Count: ", count)
print("executing bulk")
Student.objects.bulk_create(final_bulk_students)
print("complete")
print("fcount: ", fcount)
print("count: ", count)
