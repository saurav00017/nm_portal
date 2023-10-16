import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from datarepo.models import Branch
from datarepo.models import District
from datarepo.models import AffiliatedUniversity





count = 0
ncount = 0
file = open(os.path.join(settings.BASE_DIR, 'scripts/colleges/degree/degree_colleges_nov_11_1.csv'))
csv_data = csv.reader(file)
for record in csv_data:
    affiliated_university = record[1].strip().upper()
    college_code = str(record[0]).strip().lower() + str(record[2]).strip().lower()
    management_type = record[3]
    district = record[4].strip().upper()
    pincode = None if record[5].strip() == '' else int(record[5].strip().lower().replace(' ','').replace('.',''))
    spoc_name = record[6].strip()
    spoc_email = record[7].strip().lower()
    spoc_phone = record[8].strip()
    college_name = record[9].strip()
    address = record[10].strip()
    affiliated_university_obj = None
    college_category_id = None
    if management_type == '1':
        college_category_id = 3
    elif management_type == '2':
        college_category_id = 14
    elif management_type == '9':
        college_category_id = 17
    elif management_type == '10':
        college_category_id = 5
    elif management_type == '11':
        college_category_id = 15
    elif management_type == '12':
        college_category_id = 18
    elif management_type == '13':
        college_category_id = 19
    elif management_type == '14':
        college_category_id = 20
    
    try:
        affiliated_university_obj = AffiliatedUniversity.objects.get(name=affiliated_university)
    except AffiliatedUniversity.DoesNotExist:
        affiliated_university_obj = AffiliatedUniversity.objects.create(name=affiliated_university)
    district_obj = None
    try:
        district_obj = District.objects.get(name=district)
    except District.DoesNotExist:
        district_obj = District.objects.create(name=district)
    try:
        new_college = College.objects.get(college_code=college_code)
        count = count + 1
    except College.DoesNotExist:
        new_college = College.objects.create(
            college_code=college_code,
            affiliated_university_id = affiliated_university_obj.id,
            management_type = management_type,
            district_id = district_obj.id,
            pincode = pincode,
            college_name = college_name,
            address = address,
            status = 0,
            email = spoc_email,
            mobile = spoc_phone,
            spoc_name = spoc_name,
            college_type = 1,
            college_category_id = college_category_id,
            )
        new_college.save()
        ncount = ncount + 1

print(count,ncount)