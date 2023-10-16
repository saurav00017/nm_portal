from skillofferings.models import SKillOfferingEnrollment
from lms.models import StudentCourse


'1BF1A5A53E4F4ED92904B116D5EA2401'

sk_en = SKillOfferingEnrollment.objects.get(
    student__invitation_id = '1BF1A5A53E4F4ED92904B116D5EA2401',
    is_mandatory = 1
)
print(sk_en.skill_offering.course_name)

sub_en = StudentCourse.objects.filter(
    course__course_unique_code = '15_BigDataAnalytics',
    is_mandatory = 1
).count()

sub_en1 = StudentCourse.objects.filter(
    course__course_unique_code = '16_CloudComputingProgram',
        is_mandatory = 1
).count()
print(sub_en)
print(sub_en1)
