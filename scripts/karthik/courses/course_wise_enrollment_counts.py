from django.db.models import Count
from skillofferings.models import FeedBack, SKillOfferingEnrollment, SKillOffering
import csv
import os
from django.conf import settings


skillofferings = SKillOffering.objects.filter(is_mandatory=1)

header = ["Id", "Course name", "Knowledge Partner", "Students Count"]

with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/courses/course_wise_enrollment_count.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for skill in skillofferings:
        enrollments = SKillOfferingEnrollment.objects.filter(is_mandatory=1, skill_offering_id=skill.id, student_id__isnull=False,).distinct('student_id')
        writer.writerow([skill.id, skill.course_name, skill.knowledge_partner.name, enrollments.count()])
        print(f"{skill.id} {skill.course_name} {enrollments.count()}")
