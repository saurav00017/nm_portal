
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

index = 0

for college_code, student_data in file_data.items():
    # index += 1
    # if index > 3:
    #     break
    if college_code in db_data.keys():
        for student_id in student_data:
            if student_id not in db_data[college_code]:

                final_test_data_not_db += f'\n{college_code,student_id}'
    else:
        print("No College in DB,", college_code)
    #
    # for student_id in student_data:
    #     if college_code in db_data.keys():


final_csv_data = 'college_code,student_roll_no'

with open(os.path.join(settings.BASE_DIR, "scripts/students/student_codes_not_match.csv"), "w") as file:
    file.write(final_test_data_not_db)
    file.close()
