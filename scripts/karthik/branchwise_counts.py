from student.models import Student
from datarepo.models import Branch
import csv
import os
from django.conf import  settings

sutudents_count = []
file_name = "scripts/karthik/branch_wise_students_count.csv"

header = ['id', 'branch', 'student count','verified student count', 'unverified student count'];


branches_list = Branch.objects.values('id', 'name').filter()

for branch in branches_list:
    student_count = Student.objects.filter(rbranch_id=branch['id']).count()
    verified_student_count = Student.objects.filter(rbranch_id=branch['id']).filter(verification_status=1, is_pass_out=False).count()
    unverified_student_count = Student.objects.filter(rbranch_id=branch['id']).filter(verification_status=0, is_pass_out=False).count()
    sutudents_count.append([
        branch['id'],
        branch['name'],
        student_count,
        verified_student_count,
        unverified_student_count
    ])

with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for student in sutudents_count:
        writer.writerow(student)

