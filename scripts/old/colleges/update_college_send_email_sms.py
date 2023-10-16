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
from datetime import datetime
import http.client
import json

now = datetime.now()
new_colleges = 0
updated_colleges = 0
dup = 0
college_ids = []

header = ['college_code', 'college_name', 'student_count', 'username', 'password', 'sms_status', 'email_status',
          'timestamp', 'email', 'phone']

file_name = "college_sms_email_dump - 2nd" + str(now.strftime("%H:%M:%S")) + ".csv"
# l
count = 0
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    with open(os.path.join(settings.BASE_DIR, 'scripts/colleges/sept2_42_1.csv')) as file:
        csv_data = csv.reader(file)
        college_id = None
        for record in csv_data:
            count = count + 1
            print(count)
            try:
                college_code = record[0]
                college_name = record[1]
                mobile = record[2]
                email = record[4]
                college_info = None
                college_info = College.objects.get(
                        college_code=college_code, subscription_status=False
                    )
                college_info.college_code = college_code
                college_info.college_name = college_name
                college_info.mobile = mobile
                college_info.email = email
                college_info.save()

                updated_colleges = updated_colleges + 1
                username = "tnengg" + str(college_info.college_code)
                username = username.lower()
                password = str(random.randint(100000, 999999))
                try:
                    new_user = User.create_registered_user(
                        username=username,
                        college_id=college_info.id,
                        password=password,
                        account_role=6,
                        email='',
                        mobile='',
                    )
                    new_user.save()
                except Exception as e:
                    data = [college_info.college_code, college_info.college_name,
                            Student.objects.filter(college_id=college_info.id).count(), username,
                            password, 'Username error False', str(e), str(datetime.now().strftime("%H:%M:%S")), email,
                            mobile]
                    writer.writerow(data)
                    continue

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
                is_email_sent = None
                try:
                    conn.sendmail(sender, [email], msg.as_string())
                    college_info.status = 1
                    college_info.subscription_status = True
                    college_info.save()
                    is_email_sent = True
                    college_ids.append(college_info.id)
                except Exception as e:
                    print(str(e))
                    is_email_sent = False
                finally:
                    conn.quit()
                is_sms_sent = None
                if mobile is not None:
                    try:
                        conn = http.client.HTTPConnection("digimate.airtel.in:15181")
                        payload = json.dumps({
                            "keyword": "DEMO",
                            "timeStamp": "1659688504",
                            "dataSet": [
                                {
                                    "UNIQUE_ID": "16596885049652",
                                    "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                    "OA": "NMGOVT",
                                    "MSISDN": "91" + str(mobile),
                                    "CHANNEL": "SMS",
                                    "CAMPAIGN_NAME": "tnega_u",
                                    "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                    "USER_NAME": "tnega_tnsd",
                                    "DLT_TM_ID": "1001096933494158",
                                    "DLT_CT_ID": "1007269191406004910",
                                    "DLT_PE_ID": "1001857722001387178"
                                }
                            ]
                        })
                        headers = {
                            'Content-Type': 'application/json'
                        }

                        conn.request("GET", "/BULK_API/InstantJsonPush", payload, headers)
                        res = conn.getresponse()
                        data = res.read()
                        sms_response = data.decode("utf-8")
                        if sms_response == 'true':
                            is_sms_sent = True
                        else:
                            is_sms_sent = False
                    except ConnectionRefusedError:
                        time.sleep(120)
                        try:
                            conn = http.client.HTTPConnection("digimate.airtel.in:15181")
                            payload = json.dumps({
                                "keyword": "DEMO",
                                "timeStamp": "1659688504",
                                "dataSet": [
                                    {
                                        "UNIQUE_ID": "16596885049652",
                                        "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                        "OA": "NMGOVT",
                                        "MSISDN": "91" + str(mobile),
                                        "CHANNEL": "SMS",
                                        "CAMPAIGN_NAME": "tnega_u",
                                        "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                        "USER_NAME": "tnega_tnsd",
                                        "DLT_TM_ID": "1001096933494158",
                                        "DLT_CT_ID": "1007269191406004910",
                                        "DLT_PE_ID": "1001857722001387178"
                                    }
                                ]
                            })
                            headers = {
                                'Content-Type': 'application/json'
                            }
                            # added
                            conn.request("GET", "/BULK_API/InstantJsonPush", payload, headers)
                            res = conn.getresponse()
                            data = res.read()
                            sms_response = data.decode("utf-8")
                            if sms_response == 'true':
                                is_sms_sent = True
                            else:
                                is_sms_sent = False
                        except ConnectionRefusedError as e:
                            is_sms_sent = False
                else:
                    is_sms_sent = False
                data = [college_info.college_code, college_info.college_name,
                        Student.objects.filter(college_id=college_info.id).count(), username,
                        password, is_sms_sent, is_email_sent, str(datetime.now().strftime("%H:%M:%S")), email, mobile]
                writer.writerow(data)

            except College.DoesNotExist:
                # college_info = College.objects.create(
                #     college_code=college_code,
                #     college_name=college_name,
                #     mobile=mobile,
                #     email=email,
                # )
                new_colleges = new_colleges + 1
                data = [record[0], record[1],
                        Student.objects.filter(college_id=None).count(), 'college does not exist in db',
                        "college does not exist", 'college does not exist', "college does not exist",
                        str(datetime.now().strftime("%H:%M:%S")), email,
                        mobile]
                writer.writerow(data)
            except MultipleObjectsReturned:
                colleges_info = College.objects.filter(
                    college_code=college_code
                ).order_by('-id')

                college_info = colleges_info.first()
                college_info.college_code = college_code
                college_info.college_name = college_name
                college_info.mobile = mobile
                college_info.email = email
                college_info.save()

                username = "tnengg" + str(college_info.college_code)
                username = username.lower()
                password = str(random.randint(100000, 999999))
                try:
                    new_user = User.create_registered_user(
                        username=username,
                        college_id=college_info.id,
                        password=password,
                        account_role=6,
                        email='',
                        mobile='',
                    )
                    new_user.save()
                except Exception as e:
                    data = [college_info.college_code, college_info.college_name,
                            Student.objects.filter(college_id=college_info.id).count(), username,
                            password, 'Username error False', str(e), str(datetime.now().strftime("%H:%M:%S")), email,
                            mobile]
                    writer.writerow(data)
                    continue
                dup = dup + 1

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
                is_email_sent = None
                try:
                    conn.sendmail(sender, [email], msg.as_string())
                    college_info.status = 1
                    college_info.subscription_status = True
                    college_info.save()
                    is_email_sent = True
                    college_ids.append(college_info.id)
                except Exception as e:
                    print(str(e))
                    is_email_sent = False
                finally:
                    conn.quit()
                is_sms_sent = None
                if mobile is not None:
                    try:
                        conn = http.client.HTTPConnection("digimate.airtel.in:15181")
                        payload = json.dumps({
                            "keyword": "DEMO",
                            "timeStamp": "1659688504",
                            "dataSet": [
                                {
                                    "UNIQUE_ID": "16596885049652",
                                    "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                    "OA": "NMGOVT",
                                    "MSISDN": "91" + str(mobile),
                                    "CHANNEL": "SMS",
                                    "CAMPAIGN_NAME": "tnega_u",
                                    "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                    "USER_NAME": "tnega_tnsd",
                                    "DLT_TM_ID": "1001096933494158",
                                    "DLT_CT_ID": "1007269191406004910",
                                    "DLT_PE_ID": "1001857722001387178"
                                }
                            ]
                        })
                        headers = {
                            'Content-Type': 'application/json'
                        }

                        conn.request("GET", "/BULK_API/InstantJsonPush", payload, headers)
                        res = conn.getresponse()
                        data = res.read()
                        sms_response = data.decode("utf-8")
                        if sms_response == 'true':
                            is_sms_sent = True
                        else:
                            is_sms_sent = False
                    except ConnectionRefusedError:
                        time.sleep(120)
                        try:
                            conn = http.client.HTTPConnection("digimate.airtel.in:15181")
                            payload = json.dumps({
                                "keyword": "DEMO",
                                "timeStamp": "1659688504",
                                "dataSet": [
                                    {
                                        "UNIQUE_ID": "16596885049652",
                                        "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                        "OA": "NMGOVT",
                                        "MSISDN": "91" + str(mobile),
                                        "CHANNEL": "SMS",
                                        "CAMPAIGN_NAME": "tnega_u",
                                        "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                        "USER_NAME": "tnega_tnsd",
                                        "DLT_TM_ID": "1001096933494158",
                                        "DLT_CT_ID": "1007269191406004910",
                                        "DLT_PE_ID": "1001857722001387178"
                                    }
                                ]
                            })
                            headers = {
                                'Content-Type': 'application/json'
                            }
                            # added
                            conn.request("GET", "/BULK_API/InstantJsonPush", payload, headers)
                            res = conn.getresponse()
                            data = res.read()
                            sms_response = data.decode("utf-8")
                            if sms_response == 'true':
                                is_sms_sent = True
                            else:
                                is_sms_sent = False
                        except ConnectionRefusedError as e:
                            is_sms_sent = False
                else:
                    is_sms_sent = False
                data = [college_info.college_code, college_info.college_name,
                        Student.objects.filter(college_id=college_info.id).count(), username,
                        password, is_sms_sent, is_email_sent, str(datetime.now().strftime("%H:%M:%S")), email, mobile]
                writer.writerow(data)
                dup_info = College.objects.filter(
                    college_code=college_code
                ).exclude(id=college_info.id).delete()
                time.sleep(0.3)

print(updated_colleges, new_colleges, dup, college_ids)
# nwe