from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOffering
from college.models import College
college_codes = []
import os
import csv
from django.conf import settings
f = open(os.path.join(settings.BASE_DIR, "scripts/mandatory/mandatory_sem_counter.csv"), 'w')
writer = csv.writer(f)
with open('scripts/mandatory/372.csv', 'r') as file:
    data = file.read()
    college_codes = str(data).split("\n")
    print(college_codes)

print(len(college_codes))

college_ids = College.objects.values_list('id', flat=True).filter(college_code__in=college_codes)
mandatory_courses = MandatoryCourse.objects.filter(college_id__in=college_ids)

sems = mandatory_courses.values_list('sem', flat=True)
print(sems)
sems = list(set(sems))
print(sems)
final_data = []

headers = ['sem', 'student_count']
writer.writerow(headers)
for sem in sems:
    skill_offering_ids = mandatory_courses.values_list('skill_offering_id', flat=True).filter(sem=sem)
    college_ids = mandatory_courses.values_list('college_id', flat=True).filter(sem=sem)
    enrolment_count = SKillOfferingEnrollment.objects.filter(
        skill_offering_id__in=skill_offering_ids,
        is_mandatory=1,
        student__college_id__in=college_ids
    ).count()
    writer.writerow([sem, enrolment_count])

enrolment_count_3rd_sem = SKillOfferingEnrollment.objects.filter(
        student__sem=3,
        is_mandatory=1,
        student__college_id__in=college_ids
    ).count()

writer.writerow([3, enrolment_count_3rd_sem])

