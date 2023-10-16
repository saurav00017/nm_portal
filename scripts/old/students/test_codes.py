from student.models import Student
import os
import csv
from college.models import College
from django.db.models import Count
import json
from django.conf import settings

# def file_data():
#     file = open(os.path.join(settings.BASE_DIR, 'scripts/students/STUDLIST_200822.csv'))
#     csv_data = csv.reader(file)
#     students_data_from_file_data = {}
#     counter = 0
#     for record in csv_data:
#         try:
#             college_code = str(record[0])
#             student_roll_no = str(record[2])
#             # print(student_roll_no)
#
#             if college_code in students_data_from_file_data.keys():
#                 students_data_from_file_data[college_code].append(student_roll_no)
#             else:
#                 students_data_from_file_data[college_code] = [student_roll_no]
#             counter += 1
#         except Exception as e:
#             print(e)
#
#     with open(os.path.join(settings.BASE_DIR, 'scripts/students/data_check_code_dir.json'), 'w') as json_file:
#         json_file.write(json.dumps(students_data_from_file_data))
#         json_file.close()
#     file.close()
#     return counter
#
#
# print("File Count", file_data())

def db_student():
    counter = 0
    college_ids = College.objects.annotate(std_sum=Count('student')).filter(std_sum__gte=1)
    db_students_data = Student.objects.values_list('college__college_code', 'roll_no').filter(college_id__in=college_ids)

    db_student_records = {}
    db_count = 0

    for record in db_students_data:
        college_code = str(record[0])
        roll_no = str(record[1])
        if college_code in db_student_records:
            db_student_records[college_code].append(roll_no)
        else:
            db_student_records[college_code] = [roll_no]
        db_count += 1

    with open(os.path.join(settings.BASE_DIR, 'scripts/students/data_check_db_dir.json'), 'w') as json_file:
        json_file.write(json.dumps(db_student_records))
        json_file.close()
    return counter


print("DB Count", db_student())
