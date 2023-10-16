import os
import csv
from django.conf import settings
from lms.models import StudentCourse, LMSClient
from skillofferings.models import SKillOfferingEnrollment
from django.db.models import Q
file = open(os.path.join(settings.BASE_DIR, "scripts/new/lms/lms_junk_data1.csv"), 'w')
writer = csv.writer(file)

writer.writerow([
    "lms_client",
    "course_code",
    "course_name",
    "college_code",
    "student_id",
    "subscription_reference_id",
    "subscription_on",
    "created",

])

skill_offering_enrollments = SKillOfferingEnrollment.objects.select_related('skill_offering').filter(
    Q(Q(skill_offering__lms_course__isnull=False) | Q(lms_course__isnull=False)),
)

student_course_ids = []
total_count = skill_offering_enrollments.count()
for index, enrolled in enumerate(skill_offering_enrollments):
    try:
        student_course = StudentCourse.objects.values('id').get(
            Q(
                Q(course_id=enrolled.skill_offering.lms_course_id if enrolled.skill_offering_id else None)|
                Q(course_id=enrolled.lms_course_id)
            ),
            student_id=enrolled.student_id,
        )
        student_course_ids.append(student_course['id'])
    except StudentCourse.MultipleObjectsReturned:
        student_courses = StudentCourse.objects.values('id').filter(
            Q(
                Q(course_id=enrolled.skill_offering.lms_course_id if enrolled.skill_offering_id else None)|
                Q(course_id=enrolled.lms_course_id)
            ),
            student_id=enrolled.student_id,
        )
        for record in student_courses:
            student_course_ids.append(record['id'])
    except Exception as e:
        print("Error :", str(e))
    print("Pending:", total_count-index-1)

final_student_course_list = StudentCourse.objects.select_related('lms_client', 'course', 'student', 'student__college').values_list(
    'lms_client__client',
    'course__course_unique_code',
    'course__course_name',
    'student__college__college_code',
    'student__invitation_id',
    'subscription_reference_id',
    'subscription_on',
    'created'
).all().exclude(id__in=student_course_ids).order_by('lms_client__client', 'student__college__college_code')

writer.writerows(list(final_student_course_list))





