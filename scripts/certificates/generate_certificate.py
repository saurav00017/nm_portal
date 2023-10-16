from skillofferings.models import SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
import csv
import os
from django.conf import settings


# export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/kp_counter.csv'), 'w')
# writer = csv.writer(export_file)
kp_list = SKillOfferingEnrollment.objects.filter(
    is_mandatory=1,
).distinct('skill_offering__knowledge_partner_id', 'skill_offering__knowledge_partner__name').values(
    'skill_offering__knowledge_partner_id',
    'skill_offering__knowledge_partner__name',
)

skill_offering_list = SKillOffering.objects.filter(is_mandatory=1).order_by(
    'knowledge_partner_id',
    'course_name'
)

partners_list = skill_offering_list.values('knowledge_partner__name', 'knowledge_partner_id').order_by(
    'knowledge_partner_id',
    'knowledge_partner__name',
).distinct(
    'knowledge_partner_id',
    'knowledge_partner__name',
)

total_partners_count = partners_list.count()
for i, _kp in enumerate(partners_list):
    kp_id = _kp['knowledge_partner_id']
    kp_name = str(_kp['knowledge_partner__name']).replace(" ", '_')

    total_count = skill_offering_list.filter(knowledge_partner_id=_kp['knowledge_partner_id']).count()
    for sk_index, skill_offering in enumerate(skill_offering_list.filter(knowledge_partner_id=_kp['knowledge_partner_id'])):
        course_name = skill_offering.course_name
        partner = skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else None
        enrollments = SKillOfferingEnrollment.objects.filter(
            is_mandatory=1,
            skill_offering_id=skill_offering.id,
            student_id__isnull=False
        ).distinct(
            'skill_offering_id',
            'student_id'
        ).values('skill_offering_id', 'student_id')

        zero_counter = 0
        more_than_100 = 0
        enrollment_count = enrollments.count()
        for enroll_index, enrollment in enumerate(enrollments):
            progress = SKillOfferingEnrollmentProgress.objects.filter(
                skill_offering_enrollment__skill_offering_id=enrollment['skill_offering_id'],
                skill_offering_enrollment__student_id=enrollment['student_id'],
            ).order_by('-created').first()
            print(f"{kp_name}  Pending ---> {total_partners_count - i} ---> {total_count - sk_index} ------> {enrollment_count - enroll_index}")
            if progress:
                if progress.progress_percentage > 50:
                    progress.save()

