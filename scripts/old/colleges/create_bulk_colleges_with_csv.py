import csv
import os.path
import os
from college.models import College
from users.models import User, UserDetail
from datarepo.models import AccountRole
import uuid
import json
from django.conf import settings


def get_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1]


def get_password_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1][:8]


success_data = []
failed_data = []
file = open(os.path.join(settings.BASE_DIR, 'scripts/nm_colleges.csv'))
csv_data = csv.reader(file)
counter = 0
for record in csv_data:

    college_name = record[0]
    college_code = record[1]
    email = record[2]
    print(college_name, email)
    if '@' in str(email) and len(str(college_name)) > 4:
        counter += 1
        if counter > 50:
            break
        username = email.split("@")[0]
        password = get_password_uid()
        new_college = College.objects.create(
            invitation_id=get_uid(),
            status=2,
            college_name=college_name,
            email=email,
            college_code=college_code,
        )

        new_user = User.create_registered_user(
            username=username,
            password=password,
            mobile="0123456789",
            email=email,
            account_role=AccountRole.COLLEGE_ADMIN,
            college_id=new_college.id
        )
        success_data.append({
            "college_name": college_name,
            "email": email,
            "new_user": new_user.username,
            "password": password,
            "college_id": new_college.id,
        })
    else:
        failed_data.append({
            "college_name": college_name,
            "email": email,
        })

context = {
    "success": success_data,
    "failed": failed_data,
}
print(json.dumps(context))
