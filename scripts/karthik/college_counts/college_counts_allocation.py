from college.models import College
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
from student.models import Student
import os
from django.conf import  settings

collegeCodes = ["1101","1105","1108","1111","1120","1123","1124","1125","1126","1127","1128","1133","2101","2102","2105","2106","2109","2111","2113","2117","2119","2120","2124","2126","2128","1114","2115","2129","5134","1106","2112","1","2104","1107","1138","2108","3101","3107","3108","3110","3115","3116","3118","3128","3105","3114","3111","2","3103","3121","3125","4101","4103","4106","4107","4108","4114","4115","4116","4117","4118","4120","4121","4123","4126","4127","4130","4"]

header = ["College Name", "College Code", "Students Count", "Mandatory Eligible Count", "Mandatory Allocated Count", "Allocation Finished"]


with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/college_counts/college_allocations.csv'), 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for code in collegeCodes:
        college = College.objects.get(college_code=code)

        courses = MandatoryCourse.objects.filter(college_id=college.id)

        students_eligible_count = 0
        students_assigned_count = 0


        branch_ids = courses.values_list('branch_id', flat=True)
        branch_ids = list(set(list(branch_ids)))
        
        for branch_id in branch_ids:
            sem_list_in_branch = courses.filter(branch_id=branch_id).values_list('sem', flat=True)
            sem_list_in_branch = list(set(list(sem_list_in_branch)))
            for sem in sem_list_in_branch:
                skill_offering_ids = courses.filter(branch_id=branch_id, sem=sem).values_list('skill_offering_id',flat=True)
                s_c = Student.objects.filter(
                    college_id=college.id,
                    rbranch_id=branch_id,
                    sem=sem
                ).count()
                students_eligible_count += s_c

                s_e_c = SKillOfferingEnrollment.objects.select_related('student').filter(
                    student__college_id=college.id,
                    student__rbranch_id=branch_id,
                    student__sem=sem,
                    skill_offering_id__in=skill_offering_ids,
                    is_mandatory=1,
                ).count()
                students_assigned_count += s_e_c
        
        student_count = Student.objects.filter(college_id=college.id).count()

        students_assigned_count = SKillOfferingEnrollment.objects.filter(college_id=college.id, is_mandatory=1).count()
        print(students_assigned_count)

        writer.writerow([college.college_name, college.college_code, student_count, students_eligible_count, students_assigned_count, 'YES' if college.course_allocation == 1 else 'NO'])

