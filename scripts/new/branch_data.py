from college.models import College
from student.models import Student
from django.db.models import F
from datarepo.models import CollegeType, Branch
import os
import os
from django.conf import  settings
file_name = "scripts/new/branch_data_with_student.csv"
branch_list = Branch.objects.values('id', 'name').all()

csv_data = 'id,branch,student count'

for branch in branch_list:
    csv_data += f"\n" \
                f"{branch['id']}," \
                f"{branch['name']}," \
                f"{Student.objects.filter(rbranch_id=branch['id']).count()}"

with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
    f.write(csv_data)
    f.close()