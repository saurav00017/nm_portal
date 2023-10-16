
import os
import os
import csv
from college.models import College
from django.db.models import Count
import json
from django.conf import settings

file_data = {}
db_data = {}

with open(os.path.join(settings.BASE_DIR, 'scripts/students/data_check_code_dir.json'), "r") as file:
    file_data = json.loads(file.read())
    file.close()

with open(os.path.join(settings.BASE_DIR, 'scripts/students/data_check_db_dir.json'), "r") as file:
    db_data = json.loads(file.read())
    file.close()

final_test_data_not_db = 'code,roll_no'
file_college_codes = file_data.keys()
db_college_codes = db_data.keys()

colleges_codes_not_match = []

colleges_codes_not_match += list(set(file_college_codes) - set(db_college_codes))
colleges_codes_not_match += list(set(db_college_codes) - set(file_college_codes))
colleges_codes_not_match = set(colleges_codes_not_match)

students_not_match = 'college_code,student_roll_no,not_match'
students_not_match_data = {}

# print("flag 3")
# Step 1
final_check_data = {}
for college_code in file_college_codes:
    check_data = []
    file_students = file_data[college_code] if college_code in file_data.keys() else []
    db_students = file_data[college_code] if college_code in db_data.keys() else []

    student_codes_not_match = []
    student_codes_not_match += list(set(file_students) - set(db_students))
    student_codes_not_match += list(set(db_students) - set(file_students))
    student_codes_not_match = set(student_codes_not_match)
    final_check_data[college_code] = list(student_codes_not_match)


# print("flag 4")
final_check_data_codes = final_check_data.keys()
for college_code in db_college_codes:
    check_data = []
    # print("floag - 12")
    print(college_code in file_data.keys())
    print(college_code in db_data.keys())
    file_students = file_data[college_code] if college_code in file_data.keys() else []

    # print("floag - 164")
    db_students = db_data[college_code] if college_code in db_data.keys() else []

    # print("floag - 1641")

    student_codes_not_match = []
    if not db_students:
        student_codes_not_match = set(file_students) if file_students else []
    if not file_students:
        student_codes_not_match = set(db_students) if db_students else []
    else:
        student_codes_not_match += list(set(file_students) - set(db_students))
        student_codes_not_match += list(set(db_students) - set(file_students))
        student_codes_not_match = set(student_codes_not_match)

    # print("floag - 1642")

    # print("floag - 143")
    if college_code in final_check_data_codes:
        final_check_data[college_code] += list(student_codes_not_match)
    else:
        final_check_data[college_code] = list(student_codes_not_match)


final_csv_data = 'college_code,student_roll_no'

for college_code, student_data in final_check_data.items():
    student_data = list(set(student_data))
    for roll_no in student_data:
        final_csv_data += f"\n{college_code},{roll_no}"

with open(os.path.join(settings.BASE_DIR, "scripts/students/student_codes_not_match.csv"), "w") as file:
    file.write(final_csv_data)
    file.close()
