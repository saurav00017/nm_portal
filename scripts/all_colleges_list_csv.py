import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datetime import datetime

#test
#test
#test
#test
#test

header = ['college_code', 'z', 'email', 'mobile', 'status', 'students_count']

file_name = "sept_7_colleges_dump" + str(datetime.now().strftime("%H:%M:%S")) + ".csv"

colleges = College.objects.filter(college_type=2)

with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for college_info in colleges:
        data = [college_info.college_code, college_info.college_name,
                college_info.email, college_info.mobile,
                college_info.status, Student.objects.filter(college_id=college_info.id).count()]
        writer.writerow(data)
