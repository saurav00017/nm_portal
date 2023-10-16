from college.models import College
from django.db.models import F
import os
from django.conf import  settings
final_bulk_students = []
file_name = "scripts/new/college_data.csv"

csv_data = 'University code,College name,District name,Email,Mobile,Spoc name,Address'

colleges_list = College.objects.annotate(district_name=F('district__name')).values(
    'college_name',
    'college_code',
    'email',
    'mobile',
    'spoc_name',
    'address',
    'district_name',
).filter(college_type=2)

for obj in colleges_list:
    csv_data += f'\n{obj["college_code"]},' \
                f'{obj["college_name"]},' \
                f'{obj["district_name"]},' \
                f'{obj["email"]},' \
                f'{obj["mobile"]},' \
                f'{obj["spoc_name"]},' \
                f'{obj["address"]}' \
                f''
with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
    f.write(csv_data)
    f.close()