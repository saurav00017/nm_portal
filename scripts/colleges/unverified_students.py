from student.models import Student
import os
import csv
from django.conf import settings

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/data/by_college_code/cousera/372.csv'))
csv_data = csv.reader(file)
college_codes_list = []
for college_code in csv_data:
    college_codes_list.append(college_code[0])
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/colleges/unverified_student_data.csv'), 'w')
writer = csv.writer(export_file)

students_list = Student.objects.filter(
    verification_status=0,
    college__college_code__in=college_codes_list
)


total_count = students_list.count()
print(total_count)

writer.writerow(['Student id', 'name', 'email', 'phone_number', 'roll no', 'College code', 'college', 'Is in 372 college'])
for idx, student in enumerate(students_list):
    print("Pending -->", total_count - idx)
    writer.writerow([
        student.invitation_id,
        student.aadhar_number,
        student.email,
        student.phone_number,
        student.roll_no,
        student.college.college_code if student.college_id else None,
        student.college.college_name if student.college_id else None,
    ])
    student.email = None
    student.phone_number = None
    student.save()
