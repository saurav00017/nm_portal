from college.models import College
import csv

college_count = College.objects.filter(course_allocation=1).count()
print(college_count)


college_not_count = College.objects.filter(course_allocation=0).count()
print(college_not_count)

header = ['college_id', 'college_code', 'college_name']


colleges = College.objects.filter(course_allocation=0)

with open('unallocated_colleges.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for college_info in colleges:
        data = [college_info.id, college_info.college_code, college_info.college_name]
        writer.writerow(data)

