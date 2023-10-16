from student.models import Student
from college.models import College
import csv

colleges_count = []
file_name = "scripts/kathik/colleges_counts.csv"

header = ['id', 'college', 'college_code', 'student count','verified student count', 'unverified student count']


college_list = College.objects.values('id', 'college_name', 'college_code').filter()

for college in college_list:
    student_count = Student.objects.filter(p=college['id']).count()
    verified_student_count = Student.objects.filter(college_id=college['id']).filter(verification_status=True).count()
    unverified_student_count = Student.objects.filter(college_id=college['id']).filter(verification_status=False).count()
    colleges_count.append([
        college['id'],
        college['college_name'],
        college['college_code'],
        student_count,
        verified_student_count,
        unverified_student_count
    ])

with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for college_info in college_list:
        writer.writerow(college_info)