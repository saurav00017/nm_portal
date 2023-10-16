import csv
import os
from django.conf import settings
from skillofferings.models import SKillOfferingEnrollment, SKillOffering
from student.models import Student
success_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/tcs/success_students.csv'), 'w')
success_writer = csv.writer(success_file)

not_found = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/tcs/not_found_students.csv'), 'w')
not_found_writer = csv.writer(not_found)

multi_stds = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/tcs/multi_students.csv'), 'w')
multi_writer = csv.writer(multi_stds)

failed_records = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/tcs/failed_students.csv'), 'w')
failed_writer = csv.writer(failed_records)
total = 2600
index = 0
with open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/tcs/TCS_2600_students.csv'), 'r') as file:
    csv_data = csv.reader(file)
    print(next(csv_data))
    for row in csv_data:

        print("Pending ", total - index)
        index += 1
        try:
            """
            1 - S.NO,
            2 - NQT ID New,
            3 - First Name,
            4 - Last Name,
            5 - Email Id,
            6 - Phone Number,
            7 - College Name,
            8 - Semester/YOP,
            9 - Category,
            10 - Final allocation,
            11 - Dept
            """
            # email = row[4]
            phone_number = row[5]
            course_name = row[9]
            student = Student.objects.get(phone_number__iexact=str(phone_number).strip().replace(" ", ""))
            print("Student", student.email)
            skill_offering = SKillOffering.objects.filter(
                knowledge_partner_id=6,  # TCS IoN
                is_mandatory=0,
                offering_type=1,
                course_name__iexact=course_name,
                lms_course__isnull=False
            ).order_by('-id').first()
            print("skill_offering", skill_offering)
            if skill_offering:
                try:
                    skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                        student_id=student.id,
                        skill_offering_id=skill_offering.id,
                        is_mandatory=0,
                    )
                    row = [student.invitation_id] + row
                    success_writer.writerow(row)
                except SKillOfferingEnrollment.DoesNotExist:
                    skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                        student_id=student.id,
                        college_id=student.college_id,
                        lms_course_id=skill_offering.lms_course_id,
                        skill_offering_id=skill_offering.id,
                        knowledge_partner_id=skill_offering.knowledge_partner_id,
                        is_mandatory=0,
                        status=4,  # approved,
                        offering_type=skill_offering.offering_type,
                        offering_kind=skill_offering.offering_kind,
                    )
                    row = [student.invitation_id] + row
                    success_writer.writerow(row)
        except Student.DoesNotExist:
            print(row)
            not_found_writer.writerow(row)
        except Student.MultipleObjectsReturned:
            multi_writer.writerow(row)
        except Exception as e:
            row += [str(e)]
            failed_writer.writerow(row)
            print("Error", row, e)


