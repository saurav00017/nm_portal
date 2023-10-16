from skillofferings.models import SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
import csv
import os
from django.conf import settings


export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/kp_counter.csv'), 'w')
writer = csv.writer(export_file)
kp_list = SKillOfferingEnrollment.objects.filter(
    is_mandatory=1,
).distinct('skill_offering__knowledge_partner_id', 'skill_offering__knowledge_partner__name').values(
    'skill_offering__knowledge_partner_id',
    'skill_offering__knowledge_partner__name',
)

writer.writerow([
    'kp_name',
    'course',
    'total_score',
    'student_id',
    'roll no',
    'name',
    'email',
    'phone number',
    'college code',
    'college',
])

skill_offering_list = SKillOffering.objects.filter(is_mandatory=1).order_by(
    'knowledge_partner_id',
    'course_name'
)

total_skill_offering_count = skill_offering_list.count()

for sk_index, skill_offering in enumerate(skill_offering_list):
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
        print(f"Pending ---> {total_skill_offering_count - sk_index} ---> {enrollment_count-enroll_index}")
        if progress:
            if progress.progress_percentage == 0 or progress.progress_percentage > 100:
                student_id = progress.skill_offering_enrollment.student.invitation_id
                student = progress.skill_offering_enrollment.student
                has_other_progress = SKillOfferingEnrollmentProgress.objects.filter(
                    skill_offering_enrollment__is_mandatory=True,
                    skill_offering_enrollment__student_id=student.id,
                ).order_by('-created').exclude(
                    skill_offering_enrollment__skill_offering_id=progress.skill_offering_enrollment.skill_offering_id).first()
                writer.writerow([
                    partner,
                    course_name,
                    progress.progress_percentage,

                    student_id,
                    student.roll_no,
                    student.aadhar_number,
                    student.email,
                    student.phone_number,
                    student.college.college_code if student.college_id else None,
                    student.college.college_name if student.college_id else None,

                    True if has_other_progress else None,
                    has_other_progress.skill_offering_enrollment.skill_offering_id if has_other_progress else None,
                    has_other_progress.skill_offering_enrollment.skill_offering.course_name if has_other_progress else None,
                    has_other_progress.progress_percentage if has_other_progress else None,

                ])