import csv
import os
from django.conf import settings
import collections
from college.models import College
from student.models import Student
from datarepo.models import CollegeType, CollegeManagementType
from datarepo.views import get_class_list

all_colleges = College.objects.filter(management_type__in=[2,4,6,7,8,11,14])


header = ['college_code', 'college_name', 'email', 'mobile', 'spoc_name', 'college_type_id',  'college_type', 
'affiliated_university', 'zone', 'management_type_id', 'management_type'
        'year_of_establishment', 'total_faculty_count', 'village', 'town_city', 'district', 
        'state', 'pincode', 'website_url', 'taluk', 'college_category'
]

header1 = ["student_id", "name", "roll_no", "branch", "semester", "email_id", "phone"]

collegeTypes = get_class_list(CollegeType)
managementTypes = get_class_list(CollegeManagementType)

with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/colleges/aut_colleges.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for c in all_colleges:
         
        mt = managementTypes[c.management_type] if c.management_type is not None else '-'
        ct = collegeTypes[c.college_type] if c.college_type is not None else '-'
        writer.writerow([
            c.college_code,
            c.college_name,
            c.email,
            c.mobile,
            c.spoc_name,
            c.college_type,
            ct if ct is not None else '-',
            c.affiliated_university.name if c.affiliated_university is not None else '-',
            c.zone.name if c.zone is not None else '-',
            c.management_type,
            mt if mt is not None else '-',
            c.year_of_establishment,
            c.total_faculty_count,
            c.village,
            c.town_city,
            c.district,
            c.state,
            c.pincode,
            c.website_url,
            c.taluk,
            c.college_category.name if c.college_category is not None else '-',
        ])