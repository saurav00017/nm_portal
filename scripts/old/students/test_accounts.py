from student.models import Student
from college.models import College
from users.models import User
import os
from django.conf import settings
from django.db.models import Count

college_list = College.objects.annotate(student_sum=Count('student')).filter(student_sum__gte=1)
users_data_csv = 'username,password,college_code,college'
index = 0
for college in college_list[:10]:
    index += 1
    print(college.college_code, "  |  ", college.college_name)
    student = Student.objects.filter(college_id=college.id).first()
    final_username = student.roll_no
    new_user = User.create_registered_user(
        username=final_username,
        password="Password@123",
        mobile="0123456789",
        email=student.email,
        account_role=8,
        student_id=student.id
    )
    final_username = new_user.username
    users_data_csv += f'\n{final_username},Password@123,{college.college_code},{college.college_name}'

with open(os.path.join(settings.BASE_DIR, 'scripts/students/student_data.csv'), "w") as file:
    file.write(users_data_csv)
    file.close()







