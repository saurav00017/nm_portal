from college.models import College
from student.models import Student
from datarepo.models import Branch
import csv
import os
from django.conf import settings

file = open(os.path.join(settings.BASE_DIR, "scripts/new/colleges/college_branch_counter.csv"), 'w')
writer = csv.writer(file)

writer.writerow(['college_code',
                 'college_name',
                 'branch_id',
                 'branch_name',
                 'students_count',
                 'verified_students_count',
                 'logged_in_students_count'])
colleges_list = College.objects.filter(college_type=2)
total_colleges_count = colleges_list.count()

for index, college in enumerate(colleges_list):
    college_code = college.college_code
    college_name = college.college_name

    complete_students_list = Student.objects.filter(college_id=college.id)
    branch_ids = complete_students_list.values_list('rbranch_id', flat=True)
    branches_list = Branch.objects.filter(id__in=branch_ids)

    for branch in branches_list:
        students_count = complete_students_list.filter(rbranch_id=branch.id).count()
        verified_students_count = complete_students_list.filter(rbranch_id=branch.id, verification_status=1).count()
        logged_in_students_count = complete_students_list.filter(rbranch_id=branch.id, registration_status__gte=12).count()
        writer.writerow([
            # 'college_code',
            college_code,
            # 'college_name',
            college_name,
            # 'branch_id',
            branch.id,
            # 'branch_name',
            branch.name,
            # 'students_count',
            students_count,
            # 'verified_students_count',
            verified_students_count,
            # 'logged_in_students_count',
            logged_in_students_count,
        ])

    print("Pending", total_colleges_count - index)
