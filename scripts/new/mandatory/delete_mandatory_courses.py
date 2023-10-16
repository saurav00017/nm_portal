from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOffering
from lms.models import StudentCourse
mandatory_courses_list = MandatoryCourse.objects.all()

total_count = mandatory_courses_list.count()
print("Total:", total_count)
for index, mandatory_course in enumerate(mandatory_courses_list):
    skill_offering_enrollments = SKillOfferingEnrollment.objects.select_related('skill_offering').filter(
        student__college_id=mandatory_course.college_id,
        student__rbranch_id=mandatory_course.branch_id,
        student__sem=mandatory_course.sem,
        skill_offering_id=mandatory_course.skill_offering_id,
    )

    for skill_enrolled in skill_offering_enrollments:
        lms_course_id = skill_enrolled.skill_offering.lms_course_id
        if lms_course_id:
            lms_student_course = StudentCourse.objects.filter(
                student_id=skill_enrolled.student_id,
                course_id=lms_course_id).exists()
            if not lms_student_course:
                skill_enrolled.delete()
        else:
            skill_enrolled.delete()

    mandatory_course.delete()
    print("Pending", total_count - index)





