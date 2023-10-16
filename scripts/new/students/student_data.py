import os
import csv
from django.conf import settings
from student.models import Student
from django.db.models import F
from users.models import UserDetail

file = open(os.path.join(settings.BASE_DIR, "scripts/new/students/complete_students_data.csv"), 'w')
writer = csv.writer(file)

'''""
1. id,roll_no,name,college_code
2. user details - only students
'''

writer.writerow(['student_id', 'name', 'roll_no', 'college_code'])

students_list = Student.objects.annotate(
    student_id=F('id'), name=F('aadhar_number'), college_code=F('college__college_code')).values_list(
    'student_id',
    'name',
    'roll_no',
    'college_code'
)

writer.writerows(list(students_list))

file2 = open(os.path.join(settings.BASE_DIR, "scripts/new/students/student_user_details_data.csv"), 'w')
writer2 = csv.writer(file2)

user_details = UserDetail.objects.filter(
    user_id__isnull=False,
    student_id__isnull=False,
).values_list(
    'user__username',
    'student_id',
    'student__aadhar_number',
    'student__college__college_code'
)

writer2.writerow(['username', 'student_id', 'name', 'college_code'])
writer2.writerows(list(user_details))
