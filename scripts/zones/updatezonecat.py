import csv
import os
import uuid
import json
from django.conf import settings
from college.models import College
from datarepo.models import Zone,CollegeCategory


file = open(os.path.join(settings.BASE_DIR, 'scripts/zones/data.csv'))
csv_data = csv.reader(file)


not_found_codes=[]
count = 0
for record in csv_data:
        count = count + 1
        college_code = record[0]
        zone_name = record[2].strip()
        college_category = record[1].strip()
        zone_info = Zone.objects.get(name=zone_name)
        cat = CollegeCategory.objects.get(name=college_category)
        try:
                college_info = College.objects.get(college_code=college_code)
                college_info.zone_id = zone_info.id
                college_info.college_category_id = cat.id
                college_info.save()
        except College.DoesNotExist:
            not_found_codes.append(college_code)
        print(count)
print(not_found_codes)

    
