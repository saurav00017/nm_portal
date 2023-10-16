import os
import csv
from django.conf import settings
from college.models import College
from student.models import Student

file = open(os.path.join(settings.BASE_DIR, "scripts/new/colleges/required_details_output.csv"), 'w')
writer = csv.writer(file)

with open(os.path.join(settings.BASE_DIR, "scripts/new/colleges/required_details.csv")) as f:
    csv_data = csv.reader(f)
    index = 0
    for record in csv_data:
        print(record)
        college_code = record[0]
        try:
            college = College.objects.get(college_code=college_code)

            new_record = [college.college_code, college.college_name, college.spoc_name, college, ]
            new_record = [
                # 'College Code',
                college.college_code,
                # 'college name ',
                college.college_name,
                # 'sopc name ',
                college.spoc_name,
                # 'spoc number ',
                '',
                # 'Student counr',
                Student.objects.filter(college_id=college.id).count(),
                # 'verified count ',
                Student.objects.filter(college_id=college.id,verification_status=1).count(),
            ]
            writer.writerow(new_record)
        except Exception as e:
            writer.writerow(record+ [str(e)])
        index += 1
        print(index)