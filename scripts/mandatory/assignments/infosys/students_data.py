from skillofferings.models import SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
import csv
import os
from django.conf import settings


# export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/kp_counter.csv'), 'w')
# writer = csv.writer(export_file)
kp_list = SKillOfferingEnrollment.objects.filter(
    knowledge_partner_id=89,
    is_mandatory=1,
).distinct('skill_offering__knowledge_partner_id', 'skill_offering__knowledge_partner__name').values(
    'skill_offering__knowledge_partner_id',
    'skill_offering__knowledge_partner__name',
)

skill_offering_list = SKillOffering.objects.filter(is_mandatory=1).order_by(
    'knowledge_partner_id',
    'course_name'
)

partners_list = skill_offering_list.values('knowledge_partner__name', 'knowledge_partner_id').filter(
    knowledge_partner_id=89,
).order_by(
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

    with open(os.path.join(settings.BASE_DIR, f'scripts/mandatory/kp_data/{kp_name}_{kp_id}.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow([
            'First name',
            'Last name',
            'Email id',
            'Phone number',
            'Is minor(yes/No)',
            'Gender',
            'Grade',
            'Institution/ University'
        ])

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
                    student_id = progress.skill_offering_enrollment.student.invitation_id
                    student = progress.skill_offering_enrollment.student
                    has_other_progress = SKillOfferingEnrollmentProgress.objects.filter(
                        skill_offering_enrollment__is_mandatory=True,
                        skill_offering_enrollment__student_id=student.id,
                    ).order_by('-created').exclude(
                        skill_offering_enrollment__skill_offering_id=progress.skill_offering_enrollment.skill_offering_id).first()
                    writer.writerow([
                        # 'First name',
                        student.aadhar_number,
                        # 'Last name',
                        '',
                        # 'Email id',
                        student.email,
                        # 'Phone number',
                        student.phone_number,
                        # 'Is minor(yes/No)',
                        None,
                        # 'Gender',
                        None,
                        # 'Grade',
                        None,
                        # 'Institution/ University'
                        student.college.college_name if student.college_id else None
                    ])


