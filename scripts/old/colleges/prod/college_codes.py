import csv
import os
from django.conf import settings
from college.models import College

count = 0

with open(os.path.join(settings.BASE_DIR, 'scripts/colleges/prod/stable_engg_data.csv')) as file:
    csv_data = csv.reader(file)
    college_id = None
    final = []
    for record in csv_data:
        final.append(record[0])
        count = count + 1

remaining_colleges = College.objects.exclude(college_code__in=final).delete()
