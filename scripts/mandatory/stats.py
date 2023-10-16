from college.models import College
from skillofferings.models import SKillOfferingEnrollment


total_colleges = College.objects.filter(course_allocation=1)
for college in total_colleges:
    print(college.college_code,college.college_name,SKillOfferingEnrollment.objects.filter(student__college__college_code=college.college_code,is_mandatory=1).count(),sep=',')

print("total count",total_colleges.count(),sep=',')