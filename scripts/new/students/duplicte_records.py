from college.models import College
from student.models import Student
import collections
import csv
from django.db.models import F, Count
import os
from django.conf import  settings
final_bulk_students = []
file_name = "scripts/new/students/duplicate_students_data.csv"

header = ['college_code','college','student name','roll no']

all_roll_nos = Student.objects.values_list('roll_no', flat=True)
print("Count: ", all_roll_nos.count())
all_roll_nos_list = list(all_roll_nos)

duplicate_rolls = [item for item, count in collections.Counter(all_roll_nos_list).items() if count > 1]
student_duplicates = Student.objects.filter(roll_no__in=duplicate_rolls).order_by('roll_no')
index = 0
total_count = student_duplicates.count()
print("Total Duplicates", total_count)

with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for student in student_duplicates:
        # csv_data = f'{student.college.college_code if student.college_id else None},' \
        #             f'{student.college.college_name if student.college_id else None},' \
        #             f'{student.aadhar_number},' \
        #             f'{student.roll_no}' \
        #             f''
        #
        writer.writerow([
            student.college.college_code if student.college_id else None,
            student.college.college_name if student.college_id else None,
            student.aadhar_number,
            student.roll_no
        ])

        index += 1
        print("Pending ", total_count - index)
#
# with open(file_name, 'w') as f:
#     f.write(csv_data)
#     f.close()

