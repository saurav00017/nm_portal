from student.models import Student

# 7th sem Eng Students


get_students_list = list(Student.objects.values('aadhar_number', 'invitation_id').filter(
    degree=2,
    sem=7
))

csv_data = 'student_name,unique_id'

for student in get_students_list:
    csv_data += f'\n{student["aadhar_number"]},{student["invitation_id"]}'

with open("/opt/nm/NM_portal_backend/nm_portal/scripts/coursera_student_data.csv", "w") as file:
    file.write(csv_data)
    file.close()
