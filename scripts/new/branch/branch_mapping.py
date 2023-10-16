from datarepo.models import Branch
from student.models import Student
import os
from django.conf import settings
import csv

filename = "scripts/new/branch/Branch_mapping.csv"

file = open(os.path.join(settings.BASE_DIR, 'scripts/new/branch/Branch_mapping_updated_1.csv'), 'w')
writer = csv.writer(file)
with open(os.path.join(settings.BASE_DIR, filename), 'r') as f:
    csv_data = csv.reader(f)

    for record in csv_data:
        print(record)
        old_branch_id = record[1]
        new_branch_id = record[2]
        update_branch_ids = None
        try:
            old_branch_id = int(old_branch_id)
            print(old_branch_id, new_branch_id)

            update_branch_ids = Student.objects.filter(rbranch_id=old_branch_id).update(rbranch_id=new_branch_id)
        except Exception as e:
            print("Error", e)
            update_branch_ids = None

        new_record = record + [update_branch_ids]
        print(new_record)
        writer.writerow(new_record)


# file = open(os.path.join(settings.BASE_DIR, filename), 'r')
# writer = csv.writer(file)
