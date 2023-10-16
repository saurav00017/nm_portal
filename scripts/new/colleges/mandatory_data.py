import csv
import os
from django.conf import settings
from college.models import College
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
from student.models import Student

file = open(os.path.join(settings.BASE_DIR, "scripts/new/colleges/mandatory_data.csv"), 'w')
writer = csv.writer(file)

writer.writerow([
                    'college code',
                    'Manditory Branch name',
                    'Manditory Sem',
                    'Total eligible students',
                    'Pending allocations for eligible students'])
with open(os.path.join(settings.BASE_DIR, "scripts/new/colleges/college_data_69.csv")) as f:
    csv_data = csv.reader(f)
    for record in csv_data:
        try:
            college_code = record[0]
            college = College.objects.get(college_code=college_code)
            mandatory_courses_list = MandatoryCourse.objects.filter(college_id=college.id)
            for mandatory_course in mandatory_courses_list:
                students_list = Student.objects.filter(college_id=college.id, sem=mandatory_course.sem, rbranch_id=mandatory_course.branch_id)

                enrolled_student_ids = SKillOfferingEnrollment.objects.values_list('student_id', flat=True).filter(
                    student_id__in=students_list.values_list('id', flat=True),
                    skill_offering_id=mandatory_course.skill_offering_id
                )
                writer.writerow([
                    # college code
                    college_code,
                    # Manditory Branch name
                    mandatory_course.branch.name if mandatory_course.branch else None,
                    # Manditory Sem
                    mandatory_course.sem,
                    # Total eligible students
                    students_list.count(),
                    # Pending allocations for eligible students
                    students_list.exclude(id__in=enrolled_student_ids).count()
                ])
            """
            college code
            Manditory Branch name
            Manditory Sem
            Total eligible students 
            Pending allocations for eligible students
            """

        except Exception as e:
            print(e)
