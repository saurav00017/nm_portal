from student.models import Student
from college.models import College
import csv
import os
from django.conf import  settings

colleges_count = []
file_name = "scripts/karthik/colleges_counts.csv"

header = ['id', 'college', 'college_code', 'student count','verified student count', 'unverified student count'];


college_list = College.objects.values('id', 'college_name', 'college_code').filter()

for college in college_list:
    student_count = Student.objects.filter(college_id=college['id']).count()
    verified_student_count = Student.objects.filter(college_id=college['id']).filter(verification_status=1, is_pass_out=False).count()
    unverified_student_count = Student.objects.filter(college_id=college['id']).filter(verification_status=0, is_pass_out=False).count()
    colleges_count.append([
        college['id'],
        college['college_name'],
        college['college_code'],
        student_count,
        verified_student_count,
        unverified_student_count
    ])

with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for college_info in colleges_count:
        writer.writerow(college_info)

