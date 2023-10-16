from college.models import College
from django.db.models import F
from datarepo.models import CollegeType
import os
import os
from django.conf import  settings
file_name = "scripts/new/college_data_eng.csv"
def get_class_list(Class):
    items = Class.__dict__.items()
    items = filter(lambda key: not key[0].startswith("_"), items)
    items = dict(items)
    return {v: str(k).replace("_", " ") for k, v in sorted(items.items(), key=lambda item: item[1])}

college_types = get_class_list(CollegeType)
college_list = College.objects.values('id', 'college_name', 'college_code', 'college_type').filter(college_type=2)

csv_data = 'id,college code,college code,college type'

for college in college_list:
    csv_data += f"\n" \
                f"{college['id']}," \
                f"{college_types[college['college_type']] if college['college_type'] else ''}," \
                f"{college['college_code']}," \
                f"{str(college['college_name']).replace(',', '-')}" \
                f""

with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
    f.write(csv_data)
    f.close()