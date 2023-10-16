import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from datarepo.models import District
from datetime import datetime

header = ['college_code', 'college_name', 'email', 'mobile', 'email_sent', 'first_login']

file_name = "fucked_up_sept_3_college_dump_" + str(datetime.now().strftime("%H:%M:%S")) + ".csv"

file = open(os.path.join(settings.BASE_DIR, 'scripts/SPOC_PENDING_pranay_workbook.csv'))
csv_data = csv.reader(file)
counter = 0
exist = 0
not_exist = 0
not_exist_l = []
multiple_college = []

with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for record in csv_data:
        counter = counter + 1
        #rerwe
        try:
            college_info = College.objects.get(college_code=record[0])
            exist = exist + 1
        except College.DoesNotExist:
            not_exist = not_exist + 1
            not_exist_l.append(record[0])
        except College.MultipleObjectsReturned:
            multiple_college.append(record[0])
        first_login = True if college_info.status == 2 else False
        email_sent = True if college_info.subscription_status else False
        data = [college_info.college_code, college_info.college_name,
                college_info.email, college_info.mobile,
                email_sent, first_login]
        writer.writerow(data)

print("total ", counter, " exist ", exist, " not exist ", not_exist)
print("not exist ", not_exist_l)
print(multiple_college)
