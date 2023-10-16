from django.db.models import Count
from skillofferings.models import FeedBack, SKillOfferingEnrollment, SKillOffering
import csv
import os
from django.conf import settings


skillofferings = SKillOffering.objects.filter(is_mandatory=1)

header = ["Course name", "Knowledge Partner", "Students Count" "College Code", "College Name"]

with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/courses/course_colleges_data.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for skill in skillofferings:
        if skill.id != 2215:
            enrollments = SKillOfferingEnrollment.objects\
            .filter(is_mandatory=1, skill_offering_id=skill.id, student_id__isnull=False,)\
            .distinct('college_id')
            for enrollment in enrollments:
                count = SKillOfferingEnrollment.objects\
                    .filter(is_mandatory=1, skill_offering_id=skill.id, student_id__isnull=False, college_id=enrollment.college.id)\
                    .count()
                writer.writerow([skill.course_name, skill.knowledge_partner.name, count, enrollment.college.college_code, enrollment.college.college_name])
            print(f"{skill.id} {skill.course_name} {enrollments.count()}")
