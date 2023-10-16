from skillofferings.models import SKillOfferingEnrollmentProgress, SKillOfferingEnrollment, MandatoryCourse
from college.models import College
from student.models import Student
from lms.models import StudentCourse
import csv
college_filename = 'scripts/mandatory/sa/z170.csv'
college_codes = []
with open('/opt/nm/NM_portal_backend/nm_portal/' + college_filename, 'r') as file:
    data = csv.reader(file)
    for record in data:
        if record:
            college_code = record[0]
            if college_code:
                college_codes.append(college_code)

colleges = College.objects.filter(college_code__in=college_codes)
college_ids = colleges.values_list('id', flat=True)
print(f"College count: {len(college_ids)}")
students_count =Student.objects.filter(college_id__in=college_ids).count()
print(f"Student Count: {students_count}")
skill_offering_id = 2226

mandatory_courses_list = MandatoryCourse.objects.filter(
    skill_offering_id=skill_offering_id,
    college_id__in=college_ids,
).distinct('college_id', 'skill_offering_id')

print('mandatory_courses_list', mandatory_courses_list.count())
# print('unique mandatory_courses_list', mandatory_courses_list.distinct('college_id').count())
# print('unique mandatory_courses_list', mandatory_courses_list.distinct('skill_offering_id').count())
total_count = 0
enrollment_count = 0
subscribe_count = 0
# for college in colleges:
#
#     # if not MandatoryCourse.objects.filter(skill_offering_id=skill_offering_id, college_id=college.id).exists():
#         # print("------------------------")
        # print(f"College ID: {college.id}")
        # print(f"College Code: {college.college_code}")
        # print(f"College Nmae: {college.college_name}")
        # print("\n")
student_unique_ids = []

for record in mandatory_courses_list:
    total_count += record.count


    # print(record.skill_offering_id)
    enrollment_records = SKillOfferingEnrollment.objects.filter(
        skill_offering_id=record.skill_offering_id,
        student__college_id=record.college_id,
        is_mandatory=1
    )
    # update_progress = SKillOfferingEnrollmentProgress.objects.filter(
    #     skill_offering_enrollment_id__in=enrollment_records.values_list('id', flat=True)
    # ).update(assessment_data=None)
    enrollment_records= enrollment_records.distinct('skill_offering_id', 'student__invitation_id')
    enrollment_count += enrollment_records.count()
    student_course_records = StudentCourse.objects.filter(
        course_id=record.skill_offering.lms_course_id,
        student__college_id=record.college_id,
    ).distinct('course_id', 'student__invitation_id')
    subscribe_count += student_course_records.count()
    student_unique_ids += student_course_records.values_list('student__invitation_id', flat=True)

# with open('/opt/nm/NM_portal_backend/nm_portal/scripts/new/lms/ingage/student_ids1.csv', 'w') as f:
#     f.write(','.join(list()))

# print("mandatory_courses_list", total_count)
print("enrollment_count", enrollment_count)
print("subscribe_count", subscribe_count)
