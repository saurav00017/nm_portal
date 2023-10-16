import csv
import os
from django.conf import settings
from college.models import College
from student.models import Student
from users.models import UserDetail, User
import random
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText
from email.utils import formatdate
import time

# count = 0
#
# """"
# 1. update spoc email , spoc mobile if college did not login  - complete
# 2. compare 379 colleges code with my database and let vignhes sir know if any college is missing  - complete
# 3. if student records are zero do not send mail
#         --> zero students
#         --> email already sent
#         --> already logged in
# 4. if students are more then zero and college did not login send and email.
#
# """
#
# updated_college_codes = []
# not_found_college_codes = []
# duplicate_colleges = []
# with open(os.path.join(settings.BASE_DIR, 'scripts/colleges/prod/new_set1.csv')) as file:
#     csv_data = csv.reader(file)
#     for record in csv_data:
#         try:
#             check_college = College.objects.get(college_code=record[1])
#             if check_college.status == 0:
#                 check_college.email = record[5]
#                 check_college.mobile = record[4]
#                 check_college.save()
#                 # 1 - close
#                 updated_college_codes.append(record[1])
#         except College.DoesNotExist:
#             not_found_college_codes.append(record[1])
#         except College.MultipleObjectsReturned:
#             duplicate_colleges.append(record[1])
#             # 2 close

# colleges_codes_list = []
# colleges = College.objects.filter(
#     status=0
# )
# for college in colleges:
#     students_count = Student.objects.filter(college_id=college.id).count()
#     if students_count >= 1:
#         colleges_codes_list.append(college.college_code)
#
# # dont forget about colleg3e type =2
#
#
# colleges_list = College.objects.filter(status=0, college_code__in=colleges_codes_list)
# print("total colleges to which we have to send mail ", colleges_list.count())


# print("updated_college_codes", updated_college_codes)
# print("not_found_college_codes", not_found_college_codes)
# print("duplicate_colleges", duplicate_colleges)
# print("updated_college_count", len(updated_college_codes))
# print("not_found_college_count", len(not_found_college_codes))
# print("duplicate_colleges_count", len(duplicate_colleges))

count = 0
college_ids = []
for college in colleges_list:
    email = college.email
    username = "tnengg" + str(college.college_code)
    username = username.lower()
    password = str(random.randint(100000, 999999))
    new_user = User.create_registered_user(
        username=username,
        mobile='0123456789',
        email='',
        college_id=college.id,
        password=password,
        account_role=6
    )
    new_user.save()

    SMTPserver = 'mail.tn.gov.in'
    sender = 'naanmudhalvan@tn.gov.in'

    USERNAME = "naanmudhalvan"
    PASSWORD = "*nmportal2922*"

    content = f"""\
                Dear Team,

                Greetings from  Naan Mudhalvan team. Thank you for your interest in Naan Mudhalvan programme

                Please find your URL and login credentials for Naan Mudhalvan platform

                        URL to login : https://portal.naanmudhalvan.tn.gov.in/login
                        Username : {username}
                        Password : {password}

                Please feel free to contact us on support email - support@naanmudhalvan.in

                Thanks,
                Naan Mudhalvan Team,
                Tamil Nadu Skill Development Corporation


                This is an automatically generated email from the Naan Mudhalvan Platform. Please do not reply to the sender of this email.


                """

    subject = "Invitation to Naan Mudhalvan"
    text_subtype = 'plain'
    msg = MIMEText(content, text_subtype)
    msg['Subject'] = subject
    msg['From'] = sender  # some SMTP servers will do this automatically, not all
    msg['Date'] = formatdate(localtime=True)

    conn = SMTP(host=SMTPserver, port=465)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD)

    print("sending " + str(count) + " email")
    print("username", username)
    print("password", password)
    print("count", Student.objects.filter(college_id=college.id).count())
    print("email", [email])
    try:
        conn.sendmail(sender, [email], msg.as_string())
        college.status = 1
        college.subscription_status = True
        college.save()
        print("email sent")
        college_ids.append(college.id)
    except Exception as e:
        print(str(e))
    finally:
        conn.quit()
    count = count + 1
    time.sleep(0.3)
print(college_ids)
