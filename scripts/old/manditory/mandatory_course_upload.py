import csv
import os
from django.conf import settings

file = open(os.path.join(settings.BASE_DIR, "scripts/old/manditory/data1_output.csv"), 'w')
writer = csv.writer(file)
writer.writerow([
    "College Code", "Branch code", "Sem", "course code", "Number of allocations", "Course type", "Unlimited"])
with open(os.path.join(settings.BASE_DIR, 'scripts/old/manditory/data1.csv'), 'r') as f:
    csv_data = csv.reader(f)
    index = 0
    for record in csv_data:
        # College Code,Branch code,Sem,course code,Number of allocations,Course type,Unlimited
        college_code = record[0]
        branch_id = record[1]
        sem = record[2]
        course_code = record[3]
        Number_of_allocations = record[4]
        course_type = 1 if record[5] == "Paid" else 0
        is_unlimited = True if str(record[6]).lower().strip() == 'yes' else False
        print(record)
        index += 1

        if index > 3:
            break
        record += ["Added to DB"]
        writer.writerow(record)