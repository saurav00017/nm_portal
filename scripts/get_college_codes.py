import csv
import os
from college.models import College
from django.conf import settings
from datetime import datetime
from student.models import Student

file = open('/opt/nm/NM_portal_backend/nm_portal/scripts/autonomous_engg_colleges.csv')
csv_data = csv.reader(file)
for record in csv_data:
    try:
        college_info = College.objects.get(college_code=record[0].strip())
        college_students = Student.objects.filter(college_id=college_info.id)
        print(record[0],college_info.college_name,college_students.count(),college_students.filter(verification_status=True).count(),college_students.filter(registration_status=12).count(),sep=',')
    except College.DoesNotExist:
        print(record[0],"Not in db",0,0,0)