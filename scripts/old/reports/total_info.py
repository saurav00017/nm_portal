from college.models import College
from student.models import Student
from django.db.models import Count, Q
from datarepo.models import CollegeType

college_data = College.objects.annotate(
    std_sum=Count('student', filter=Q(student__verification_status=1)),
    total_std_sum=Count('student'),
).values('college_code', 'college_name','total_std_sum').filter(
    std_sum=0
)
print("Flag 1", )
print("Flag 1")
for college in college_data:
    print(college['college_code'], college['college_name'], college['total_std_sum'], sep=',', end="\n")

print("Flag 2")
all_engineering_colleges = College.objects.filter(college_type=CollegeType.ENGINEERING)
print("1. Total engineering college - count-----------------------------", all_engineering_colleges.count())
print("2. Total engineering college invites sent  - count --------------", all_engineering_colleges.annotate(std_sum=Count('student', filter=Q(student__is_mailed=1))).filter(std_sum__gte=1).count())
print("3. Total engineering college first time login - count  ----------", all_engineering_colleges.filter(status=2).count())
print("5. Students - Verification completed colleges count   -----------", College.objects.annotate(
    std_sum=Count('student', filter=Q(student__verification_status=1))
).filter(std_sum__gt=0, is_students_verified=1).count())
print("6. Students Verification did not start count---------------------", college_data.count())
print("7. Students Partial verification College count---------------------------", College.objects.annotate(
    std_sum_verified=Count('student', filter=Q(student__verification_status=1)),
    std_sum_unverified=Count('student', filter=Q(student__verification_status=0))
).filter(std_sum_verified__gte=1,std_sum_unverified__gte=1).count())

"""
LIST

1. Total engineering college - count 

2. Total engineering college invites sent  - count 

3. Total engineering college first time login - count 

5. Students - Verification completed colleges count 

6. Students Verification did not start count 

7. Students Partial verification count
"""
