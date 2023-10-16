
import csv
import os.path
import os
from django.conf import settings
from datarepo.models import Branch

count = 0
with open(os.path.join(settings.BASE_DIR, "scripts/polystudents/polystudents_Course_Code.csv"), 'r') as file:
    csv_data = csv.reader(file)
    for record in csv_data:
        count = count + 1
        try:
            branch_id = int(record[0])
            branch_name = record[1]
            new_branch = Branch.objects.create(
                id=branch_id,
                name=branch_name
            )
            new_branch.save()
        except Exception as e:
            print("-->", record, e)
        print(count)
