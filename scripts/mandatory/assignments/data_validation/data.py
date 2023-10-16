from skillofferings.models import SKillOffering, SKillOfferingEnrollmentProgress
from django.db.models import F
import os
from django.conf import settings
import csv

all_records = SKillOfferingEnrollmentProgress.objects.select_related(
    'skill_offering_enrollment',
    'skill_offering_enrollment__skill_offering',
    'skill_offering_enrollment__skill_offering__knowledge_partner',
).filter(skill_offering_enrollment__is_mandatory=True).values_list(
    'skill_offering_enrollment__is_mandatory',
    'id',
    'progress_percentage',
    'assessment_data',
    'skill_offering_enrollment__skill_offering__ia_count',
    'skill_offering_enrollment_id',
    'skill_offering_enrollment__skill_offering_id',
    'skill_offering_enrollment__skill_offering__course_name',
    'skill_offering_enrollment__skill_offering__course_code',
    'skill_offering_enrollment__student_id',
    'skill_offering_enrollment__skill_offering__knowledge_partner_id',
    'skill_offering_enrollment__skill_offering__knowledge_partner__name',
)

file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/data_validation/assessment_data.csv'), 'w')
writer = csv.writer(file)
writer.writerow([
    'is_mandatory',
    'id',
    'progress_percentage',
    'assessment_data',
    'ia_count',
    'skill_offering_enrollment_id',
    'skill_offering_enrollment__skill_offering_id',
    'skill_offering__course_name',
    'skill_offering__course_code',
    'student_id',
    'skill_offering_enrollment__skill_offering__knowledge_partner_id',
    'skill_offering_enrollment__skill_offering__knowledge_partner__name',
])
writer.writerows(list(all_records))
