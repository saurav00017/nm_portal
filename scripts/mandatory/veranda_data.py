from skillofferings.models import SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
import csv
import os
from django.conf import settings
export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/veranda_data.csv'), 'w')
writer = csv.writer(export_file)

writer.writerow([
    'student_id',
    'course_name',
    'course_code',
])
enrollments = SKillOfferingEnrollmentProgress.objects.filter(
    progress_percentage=0,
    skill_offering_enrollment__skill_offering__knowledge_partner_id=59,
    skill_offering_enrollment__is_mandatory=True,
    skill_offering_enrollment__student_id__isnull=False,
    skill_offering_enrollment__skill_offering_id__isnull=False,
).values_list(
    'skill_offering_enrollment__student__invitation_id',
    'skill_offering_enrollment__skill_offering__course_name',
    'skill_offering_enrollment__skill_offering__course_code',
)
print(enrollments.count())

writer.writerows(list(enrollments))
