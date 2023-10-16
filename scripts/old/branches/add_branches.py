import csv
import os
import uuid
import json
from django.conf import settings
from datarepo.models import Branch
from django.db import IntegrityError



file = open(os.path.join(settings.BASE_DIR, 'scripts/old/branches/new_branches_19_sept.csv'))
csv_data = csv.reader(file)
for record in csv_data:
    try:
        branch_info = Branch.objects.create(id=record[0],name=str(record[1]).strip())
        branch_info.save()
        print(" branch created",record[0],record[1])
    except IntegrityError as e:
        print(e)
