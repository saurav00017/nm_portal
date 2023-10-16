from lms.models import StudentCourse
import os
from django.conf import settings
import csv
from skillofferings.models import SKillOfferingEnrollment, SKillOffering

headers = ['college code', 'college name', 'branch','sem','invitation_id', 'roll_no', 'email', 'course_name', 'kp_name', 'created','updated', 'skill_offering_id']

export_file = open(os.path.join(settings.BASE_DIR, 'scripts/new/lms/temp_z_none.csv'), 'w')
writer = csv.writer(export_file)

student_course_list = StudentCourse.objects.values_list(
    'student_id',
    'course_id',
    'student__college__college_code',
    'student__college__college_name',
    'student__rbranch__name',
    'student__sem',
    'student__invitation_id',
    'student__roll_no',
    'student__email',
    'course__course_name',
    'course__lms_client__client',
    'created',
    'updated',
).filter(temp_z=None)
total = student_course_list.count()
for index, std in enumerate(list(student_course_list)):
    print("Pending", total - index)
    final_std = list(std)
    try:
        skill_offering_enrolment = SKillOfferingEnrollment.objects.filter(
            student_id=std[0],
            lms_course_id=std[1],
        ).order_by('-id').first()
        if skill_offering_enrolment:
            final_std += [skill_offering_enrolment.skill_offering_id]
        else:
            try:
                skill_offering = SKillOffering.objects.filter(lms_course_id=std[1]).order_by('-id').first()
                if skill_offering:
                    final_std += [skill_offering.id]

            except Exception as e:
                print("Error ", e)
    except Exception as e:
        print("Error ", e)
    # except:
    #     pass

    writer.writerow(final_std[2:])



