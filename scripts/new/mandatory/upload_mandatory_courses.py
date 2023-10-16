from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
import os
from django.conf import settings
from college.models import College
with open(os.path.join(settings.BASE_DIR, "scripts/new/mandatory/new_mandatory.csv"), 'r') as f:
    csv_data = csv.reader(f)

    for record in csv_data:
        """
        0 College Code,
        1 Branch code,
        2 Sem,
        3. course code,
        4 Number of allocations,
        5 Course type,
        6 Unlimited 
        """
        college_code = record[0]
        branch_id = record[1]
        sem = record[2]
        course_code = record[3]
        allocation_count = record[4]
        _course_type = record[5]
        is_unlimited = record[6]

        course_type = None
        if str(_course_type).lower().strip() == "free":
            course_type = 0
        elif str(_course_type).lower().strip() == "paid":
            course_type = 1
        is_unlimited = True if str(is_unlimited).lower().strip() == "yes" else False
        try:
            get_college = College.objects.get(college_code=college_code)
            get_mandatory = MandatoryCourse.objects.get(
                college_id=get_college.id,
                branch_id=branch_id,
                sem=sem,
                skill_offering_id=course_code
            )
            get_mandatory.count=allocation_count
            get_mandatory.course_type = course_type
            get_mandatory.is_unlimited = is_unlimited
            get_mandatory.save()
        except MandatoryCourse.DoesNotExist:
            get_mandatory = MandatoryCourse.objects.create(
                college_id=get_college.id,
                branch_id=branch_id,
                sem=sem,
                skill_offering_id=course_code,
                count=allocation_count,
                course_type=course_type,
                is_unlimited=is_unlimited
            )
            get_mandatory.save()
        except Exception as e:
            print("Error", e)


