from skillofferings.models import SKillOfferingEnrollment
from student.models import Student


courses_list = SKillOfferingEnrollment.objects.filter(
    student__roll_no = 210520104302,is_mandatory=0)
print(courses_list.count())
    
