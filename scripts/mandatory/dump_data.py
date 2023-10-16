import csv
import os.path
import os
from django.conf import settings
from datarepo.models import Branch
from college.models import College
from student.models import Student
from skillofferings.models import MandatoryCourse,SKillOffering
tcount=0
scount=0
fcount=0
with open(os.path.join(settings.BASE_DIR, "scripts/mandatory/data2.csv"), 'r') as file:
    csv_data = csv.reader(file)
    for record in csv_data:
        tcount = tcount + 1
        college_code = record[0]
        branch_id = record[1]
        sem = record[2]
        course_id = record[3]
        allocations_count = record[4]

        course_type = 1 if record[5] == "Paid" else 0
        is_unlimited = True if str(record[6]).lower().strip() == 'yes' else False

        college_info = None
        branch_info = None
        course_info = None
        try:
            college_info = College.objects.get(college_code=college_code)
        except College.DoesNotExist:
            print("college_not_found",college_code,sep=',')
        try:
            branch_info = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            print("branch_not_found",branch_id,sep=',')
        try:
            course_info = SKillOffering.objects.get(id=course_id)
        except SKillOffering.DoesNotExist:
            print("course_not_found",course_id,sep=',')
        if college_info is not None and branch_info is not None and course_info is not None:
            try:
                new_m_course = MandatoryCourse.objects.create(
                    college_id = college_info.id,
                    skill_offering_id = course_info.id,
                    branch_id = branch_info.id,
                    sem = sem,
                    count = allocations_count,
		   course_type=course_type,
                   is_unlimited=is_unlimited,
                )
                new_m_course.save()
                scount = scount + 1
            except Exception as e:
                print("error",college_code,branch_id,sem,course_id,allocations_count,str(e),sep=",")
                fcount = fcount + 1
        else:
            fcount = fcount + 1

print(tcount,scount,fcount,sep=",")

36,42,47,57,62,67,80,82,137,138,143,146,7006