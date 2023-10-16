from lms.models import StudentCourse

import os
from django.conf import settings
import csv

delete_record_ids = []
with open(os.path.join(settings.BASE_DIR, "scripts/new/lms/student_course_duplicates.csv"), 'r') as file:
    csv_data = csv.reader(file)

    for row in csv_data:
        # id,student,student_name,courses_id,course,count
        try:
            student_id = row[1]
            course_id = row[3]
            print(student_id, course_id)
            if StudentCourse.objects.filter(student_id=student_id, course_id=course_id).count() > 1:
                get_non_subscribe_record = StudentCourse.objects.filter(student_id=student_id, course_id=course_id, subscription_on=None)
                for record in get_non_subscribe_record:
                    delete_record_ids.append(record.id)
                    record.delete()
        except Exception as e:
            print(row, e)
print(len(delete_record_ids))
#print(delete_record_ids)


