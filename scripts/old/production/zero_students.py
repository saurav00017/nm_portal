from college.models import College
from users.models import User
import csv
import os.path
import os
from django.conf import settings
import time
import asyncio
from io import StringIO
from django.core.exceptions import MultipleObjectsReturned
import uuid

new_colleges = 0
updated_colleges = 0
dup = 0


def get_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1]


with open(os.path.join(settings.BASE_DIR, 'scripts/production/collegedatav.csv')) as file:
    csv_data = csv.reader(file)
    college_id = None
    for record in csv_data:
        try:
            college_code = record[0]
            college_name = record[1]
            mobile = record[3]
            email = record[4]
            college_info = College.objects.get(
                college_code=college_code
            )
            college_info.college_code = college_code
            college_info.college_name = college_name
            college_info.mobile = mobile
            college_info.email = email
            college_info.status = 0
            college_info.save()
            updated_colleges = updated_colleges + 1
        except College.DoesNotExist:
            # college_info = College.objects.create(
            #     college_code=college_code,
            #     college_name=college_name,
            #     mobile=mobile,
            #     email=email,
            # )
            new_college = College.objects.create(
                invitation_id=get_uid(),
                status=0,
                college_name=college_name,
                email=email,
                college_code=college_code,
                mobile=mobile,
            )
            new_college.save()
            new_colleges = new_colleges + 1
        except MultipleObjectsReturned:
            college_info = College.objects.filter(
                college_code=college_code
            ).order_by('-id')

            first_obj = college_info.first()
            first_obj.college_code = college_code
            first_obj.college_name = college_name
            first_obj.mobile = mobile
            first_obj.email = email
            first_obj.status = 0
            first_obj.save()

            college_info = College.objects.filter(
                college_code=college_code
            ).exclude(id=first_obj.id).delete()
            dup = dup + 1

print('updated_college ', updated_colleges, 'newly added colleges ', new_colleges, 'multiple returns clean', dup)
