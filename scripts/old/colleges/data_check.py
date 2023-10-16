from college.models import College
from django.db.models import Count

colleges_list = College.objects.annotate(student_sum=Count('student')).filter(status__gte=1).order_by('student_sum')
college_data = 'college_code;college_name;student_count;status;student_verified;student_count'
index = 0
print("Total count", colleges_list.count())
for college in colleges_list:
    index += 1
    college_data += f'\n{college.college_code};{college.college_name};{college.status};{college.is_students_verified};{college.student_sum}'
    print(index, college.college_code, college.college_name, sep="  ||   ")

with open("/opt/nm/NM_portal_backend/nm_portal/scripts/college_Data_status_all.csv", "w") as file:
    file.write(college_data)
    file.close()
