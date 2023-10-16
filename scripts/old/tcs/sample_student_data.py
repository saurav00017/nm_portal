from student.models import Student
from college.models import College
from django.conf import settings
import os
import csv


file = open(os.path.join(settings.BASE_DIR, 'scripts/tcs/tcs_sample_data.csv'))
csv_data = csv.reader(file)

final_data = []
final_csv_data = 'student_id,unique_id,email'
for record in csv_data:
    try:
        college_code = record[0]
        college_name = record[1]
        student_roll_no = record[2]
        email = record[4]
        full_name = record[6]
        phone_number = record[7]
        year_of_study = record[8]
        print(email)
        try:
            get_student = Student.objects.get(
                roll_no=student_roll_no,
            )
            print(email)
            get_student.email= email
            get_student.aadhar_number= full_name
            get_student.phone_number = phone_number
            get_student.save()

            final_csv_data += f'\n{get_student.id},{get_student.invitation_id},{email}'
        except Student.DoesNotExist:
            try:
                college = College.objects.values('id').get(college_code=college_code)
                college_id = college['id']
            except:
                college_id = None
            print(student_roll_no)
            new_student = Student.objects.create(
                roll_no=student_roll_no,
                email=email,
                college_id=college_id,
                registration_status=4,
                aadhar_number=full_name,
                phone_number=phone_number,
                hall_ticket_number=student_roll_no,
                year_of_study=int(year_of_study),
            )

            final_csv_data += f'\n{new_student.id},{new_student.invitation_id},{new_student.email}'

    except Exception as e:
        print(e, record)
file.close()

with open(os.path.join(settings.BASE_DIR, 'scripts/tcs/tcs_final_data.csv'), 'w')as file:
    file.write(final_csv_data)
    file.close()
