import csv
import os
import uuid
import json
from django.conf import settings
from college.models import College


file = open(os.path.join(settings.BASE_DIR, 'scripts/zones/zone1.csv'))
csv_data = csv.reader(file)


not_found_codes=[]
count = 0
for record in csv_data:
        college_code = record[0]
        try:
                college_info = College.objects.get(college_code=college_code)
                college_info.zone_id = 1
                college_info.save()
                count = count + 1
        except College.DoesNotExist:
            not_found_codes.append(college_code)
print(count)
print(not_found_codes)

    
