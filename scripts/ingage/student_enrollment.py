from student.models import Student
from skillofferings.models import SKillOfferingEnrollment
import csv
with open('student_data.csv') as file:
    csv_data = csv.reader(file)
    print(next(csv_data))
    index = 1
    for record in csv_data:
        index += 1
        try:
            student_id = record[1]
            student = Student.objects.get(invitation_id=student_id)
            try:
                enrollment = SKillOfferingEnrollment.objects.get(
                    student_id=student.id,
                    skill_offering_id=2226
                )
                print(index, "Already Exists")
            except SKillOfferingEnrollment.DoesNotExist:
                print(index, "Created")
                enrollment = SKillOfferingEnrollment.objects.get(
                    student_id=student.id,
                    college_id=student.college_id,
                    skill_offering_id=2226,
                    lms_course_id=79,
                    knowledge_partner_id=94,
                    status=4,
                    offering_type=1,
                    offering_kind=1,
                    is_mandatory=1,
                )
            except Exception as e:
                print("Student ", student_id, "Error", e)
        except Exception as e:
            print("Exception")