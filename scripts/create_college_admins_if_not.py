import csv
import os
from django.conf import settings
from college.models import College
from student.models import Student
from datetime import datetime
import http.client
import json
import random
from users.models import User,UserDetail
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP

file = open(os.path.join(settings.BASE_DIR, 'scripts/final_college_invites.csv'))
csv_data = csv.reader(file)

header = ['college_code', 'college_name', 'student_count', 'username', 'password', 'sms_status', 'email_status',
          'timestamp', 'email', 'phone']

file_name = "fucked_up_sept_3_college_dump_" + str(datetime.now().strftime("%H:%M:%S")) + ".csv"
# l
count = 0
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for record in csv_data:
        college_code = record[0]
        username = record[2]
        password = record[3]
        email = record[7]
        mobile = record[8]
        try:
            college_info = College.objects.get(college_code=int(college_code))
            college_info.mobile = mobile
            college_info.email = email
            college_info.save()
            try:
                user_info = User.objects.get(username=username)
                user_info.set_password(password)
                user_info.save()
                try:
                    new_user_details = UserDetail.objects.get(
                        user_id=user_info.id,
                        college_id=college_info.id
                    )
                except UserDetail.DoesNotExist:
                    new_user_details = UserDetail.objects.create(
                        user_id=user_info.id,
                        college_id=college_info.id
                    )
                    new_user_details.save()
            except User.DoesNotExist:
                new_user = User.create_registered_user(
                    username=username,
                    college_id=college_info.id,
                    password=password,
                    account_role=6,
                    email='',
                    mobile='',
                )
                new_user.save()
            data = [college_info.college_code, college_info.college_name,
                    Student.objects.filter(college_id=college_info.id).count(), username,
                    password, True, True, str(datetime.now().strftime("%H:%M:%S")), email, mobile]
            writer.writerow(data)
            print("succeess")
        except College.DoesNotExist:
            data = [college_info.college_code, college_info.college_name,
                    Student.objects.filter(college_id=college_info.id).count(), username,
                    password, "NO COLLEGE IN DB", "NO COLLEGE IN DB", str(datetime.now().strftime("%H:%M:%S")), email,
                    mobile]
            writer.writerow(data)
            print("failed")
