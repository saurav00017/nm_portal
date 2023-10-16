from student.models import Student
import csv
from college.models import College
import os.path
import os
from django.conf import settings
from datetime import datetime

final_bulk_students = []
read_file_name = "scripts/new/Anna_university_SPOC_consolidated_03_09_2022.csv"
write_file_name = "scripts/new/does_not_exist_Anna_university_SPOC_consolidated_03_09_2022.csv"
total_count = 466
index = 0
with open(write_file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    with open(os.path.join(settings.BASE_DIR, read_file_name), 'r') as file:
        csv_data = csv.reader(file)
        for record in csv_data:
            index += 1
            college_code = record[3]
            spoc_name = record[5]

            try:
                college_obj = College.objects.get(college_code=college_code)
                college_obj.spoc_name = spoc_name
                college_obj.save()
            except College.DoesNotExist:
                writer.writerow(record)
            print("Pending ", total_count-index)
        # Sl. No.,Email Address  of Institution Head,TNEA Code,University Code,Name of the College,Name of the SPOC,Mobile No of SPOC,Email ID of SPOC,ref
        # 1,aktengg@yahoo.in,1441,4201,A.K.T Memorial College of Engineering and Technology,DR. A.VELMURUGAN,+91 88257 98767,principal.aktmcet@gmail.com,consolidated
print("executing bulk")
print("complete")
