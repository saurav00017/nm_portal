from lms.models import StudentCourse
from skillofferings.models import SKillOfferingEnrollment
from simple.models import SimpleCourse

simple_courses_list = SimpleCourse.objects.all()
simple_courses_count = simple_courses_list.count()
print("Total skill_offering_enrollments", simple_courses_list)

lms_course_update_count = 0
no_lms_records = 0

for index, simple_course in enumerate(simple_courses_list):
    if simple_course.lms_course_id:
        student_courses = StudentCourse.objects.filter(
            course_id=simple_course.lms_course_id,
        )
        for std_course in student_courses:
            lms_course_update_count += 1
            std_course.is_mandatory = 9
            std_course.save()
    else:
        no_lms_records += 1

    print("Pending", simple_courses_count - index)
    print("lms_course_update_count",lms_course_update_count)
    print("no_lms_records",no_lms_records)

