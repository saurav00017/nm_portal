from datarepo.models import Branch
from student.models import Student
import os
from django.conf import settings
import csv

filename = "scripts/new/branch/Engineering and Polytechnic branch_data - branch_data.csv"

branch_type_data = {}
with open(os.path.join(settings.BASE_DIR, filename), 'r') as f:
    csv_data = csv.reader(f)
    for record in csv_data:
        branch_id = record[0]
        branch_name = record[1]
        branch_type = record[2]

        if branch_type in branch_type_data:
            branch_type_data[branch_type].append(branch_id)
        else:
            branch_type_data[branch_type] = [branch_id]


for key, branch_ids in branch_type_data.items():
    print(key, len(branch_ids))
    # ARTS_AND_SCIENCE = 1
    # ENGINEERING = 2
    # ITI = 3
    # POLYTECHNIC = 4
    # PHARMA = 5
    branch_type = None
    if key == "Engineering":
        branch_type = 2
    elif key == "Polytechnic":
        branch_type = 4
    try:
        branch_db_update = Branch.objects.filter(id__in=branch_ids).update(branch_type=branch_type)
        print(key, len(branch_ids), branch_db_update)
    except:
        pass
