from lms.models import StudentCourse
from skillofferings.models import SKillOfferingEnrollment

skill_offering_enrollments = SKillOfferingEnrollment.objects.all()
skill_offering_enrollment_count = skill_offering_enrollments.count()
print("Total skill_offering_enrollments", skill_offering_enrollment_count)

lms_course_count = 0
no_lms_records = 0
for index, enrollment in enumerate(skill_offering_enrollments):
    if enrollment.skill_offering_id:
        if enrollment.skill_offering.lms_course_id:

            student_courses = StudentCourse.objects.filter(
                course_id=enrollment.skill_offering.lms_course_id,
                student_id=enrollment.student_id,
            )
            if student_courses:
                for std_course in student_courses:
                    lms_course_count += 1
                    std_course.is_mandatory = enrollment.skill_offering.is_mandatory
                    std_course.save()
            else:
                no_lms_records += 1
                print("No Student Course", enrollment.id)

    print("lms_course_count:", lms_course_count)
    print("no_lms_records:", no_lms_records)
    print("pending", skill_offering_enrollment_count- index)



