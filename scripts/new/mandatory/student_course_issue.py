from skillofferings.models import SKillOfferingEnrollment
from lms.models import StudentCourse
from users.models import UserDetail

skill_offering_enrolled_list = SKillOfferingEnrollment.objects.filter(
    is_mandatory=1, lms_course__isnull=False)

student_ids = skill_offering_enrolled_list.values_list('student_id', flat=True)

student_courses_list = StudentCourse.objects.filter(student_id__in=student_ids)

index = 0
print('skill_offering_enrolled_list', skill_offering_enrolled_list.count())
new_student_course_list = []
for enrolled in skill_offering_enrolled_list:
    try:
        check_student_course = student_courses_list.get(student_id=enrolled.student_id, course_id=enrolled.lms_course_id)
    except StudentCourse.DoesNotExist:
        index += 1
        new_student_course = StudentCourse(
            student_id=enrolled.student_id,
            course_id=enrolled.lms_course_id,
            status=1,
            lms_client_id=enrolled.lms_course.lms_client_id
        )
        new_student_course_list.append(new_student_course)

print(StudentCourse.objects.bulk_create(new_student_course_list))
print('total_count', index)