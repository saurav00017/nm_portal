import csv
import os.path
import os
from django.conf import settings
from datarepo.models import Branch
from college.models import College
from student.models import Student
from skillofferings.models import MandatoryCourse, SKillOffering, SKillOfferingEnrollment


mandatory_course_list = MandatoryCourse.objects.filter(is_unlimited=False)

for mandatory_course in mandatory_course_list:
    skill_offering_enrolled = SKillOfferingEnrollment.objects.filter(
        college_id=mandatory_course.college_id,
        student__sem=mandatory_course.sem,
        student__rbranch_id=mandatory_course.branch_id,
        skill_offering_id=mandatory_course.skill_offering_id,
    ).order_by('-created')
    if mandatory_course.count < skill_offering_enrolled.count():
        difference = skill_offering_enrolled.count() - mandatory_course.count
        print(mandatory_course.id, f'difference {difference}', f'skill_offering_enrolled {skill_offering_enrolled.count() }', mandatory_course.college_id, mandatory_course.branch_id, mandatory_course.sem , sep="  |  ")

        for enrolled in skill_offering_enrolled[:difference]:
            enrolled.delete()



