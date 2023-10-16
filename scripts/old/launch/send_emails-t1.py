import csv
from datetime import datetime
import csv
import os.path
import os
from django.conf import settings
import time
import asyncio
from io import StringIO
from django.db.models import F
from student.models import Student
from college.models import College
from users.models import User, UserDetail
import random
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText
from email.utils import formatdate
import requests
import json
import http.client
import json
from django.db import IntegrityError
import time

success_data = []
failed_data = []
bulk_students = []

now = datetime.now()

# get all verified colleges list
# students_verified_colleges_count = College.objects.filter(
#     college_type=2,
#     # status=2,
#     # is_students_verified=True,
# ).values_list('id', flat=True)

college_students = Student.objects.filter(
    # college_id__in=students_verified_colleges_count,
    college__college_type=1,
    verification_status=True
).exclude(registration_status__gte=5).order_by('id')

# latest
SMTPserver = 'mail.tn.gov.in'
sender = 'naanmudhalvan@tn.gov.in'

USERNAME = "naanmudhalvan"
PASSWORD = "*nmportal2922*"

header = ['college_code', 'roll_no', 'name', 'data_integrity_check', 'username', 'password', 'sms', 'email',
          'timestamp', 'email', 'phone']

file_name = "sms_t1_2nd_dec" + str(now.strftime("%H:%M:%S")) + ".csv"
count = 0
# l
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for student in college_students:
        if student.registration_status >= 5:
            continue
        if student.roll_no is None:
            student.registration_status == 987
            student.save()
            continue
        roll_no = (student.roll_no).replace(" ", '')
        if roll_no != '':
            college_code = student.college.college_code

            data_verified = None
            name = str(student.aadhar_number) if str(student.aadhar_number) is None else ''
            username_pref = ''
            roll_no = (student.roll_no).replace(" ", '')
            if student.college.college_type == 1:
                           
                username_pref = 'as'
            elif student.college.college_type == 2:
                if student.is_temporary_roll_number:
                    username_pref = 'aut'
                          
                username_pref = 'au'
            elif student.college.college_type == 4:
                           
                username_pref = 'p'
            username = username_pref + str(roll_no).strip()
            username = username.lower()
            password = str(random.randint(100000, 999999))
            email = [student.email]
            phone_number = str(student.phone_number)
            try:
                new_user = User.objects.create(
                    username=username,
                    account_role=8)
                new_user.save()
                new_user.set_password(password)
                new_user.save()
                student.registration_status = 5
                student.save()
                user_details = UserDetail.objects.create(
                    user_id=new_user.id,
                    student_id=student.id,
                )
                user_details.save()
                student.registration_status = 6
                student.save()

                content = f"""\
                                Dear {name},
            
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
                if student.email is None:
                    student.registration_status = 8
                    is_email_sent = False
                    student.is_mailed = False
                    student.save()
                else:
                    try:
                        conn.sendmail(sender, [email], msg.as_string())
                        is_email_sent = True
                        student.registration_status = 7
                        student.is_mailed = True
                        student.save()
                    except ConnectionRefusedError:
                        time.sleep(120)
                        try:
                            conn.sendmail(sender, [email], msg.as_string())
                            is_email_sent = True
                            student.registration_status = 7
                            student.is_mailed = True
                            student.save()
                        except ConnectionRefusedError:
                            is_email_sent = False
                            student.registration_status = 8
                            student.is_mailed = False
                            student.save()
                        except TimeoutError:
                            is_email_sent = False
                            student.registration_status = 8
                            student.is_mailed = False
                            student.save()
                        except Exception as e:
                            is_email_sent = False
                            student.registration_status = 8
                            student.is_mailed = False
                            student.save()
                        finally:
                            conn.quit()
                    except TimeoutError:
                        time.sleep(120)
                        try:
                            conn.sendmail(sender, [email], msg.as_string())
                            is_email_sent = True
                            student.registration_status = 7
                            student.is_mailed = True
                            student.save()
                        except ConnectionRefusedError:
                            is_email_sent = False
                            student.registration_status = 8
                            student.is_mailed = False
                            student.save()
                        except TimeoutError:
                            is_email_sent = False
                            student.registration_status = 8
                            student.is_mailed = False
                            student.save()
                        except Exception as e:
                            is_email_sent = False
                            student.registration_status = 8
                            student.is_mailed = False
                            student.save()
                        finally:
                            conn.quit()
                    except Exception as e:
                        is_email_sent = False
                        student.registration_status = 8
                        student.is_mailed = False
                        student.save()
                is_sms_sent = None
                if phone_number is not None:
                    try:
                        conn = http.client.HTTPConnection("digimate.airtel.in:15181")
                        payload = json.dumps({
                            "keyword": "DEMO",
                            "timeStamp": "1659688504",
                            "dataSet": [
                                {
                                    "UNIQUE_ID": "16596885049652",
                                    "MESSAGE": "Hi " + name + " , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                    "OA": "NMGOVT",
                                    "MSISDN": "91" + str(phone_number),
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
                            student.registration_status = 9
                            student.save()
                        else:
                            is_sms_sent = False
                            student.registration_status = 10
                            student.save()
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
                                        "MESSAGE": "Hi " + name + " , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                        "OA": "NMGOVT",
                                        "MSISDN": "91" + str(phone_number),
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
                                student.registration_status = 9
                                student.save()
                            else:
                                is_sms_sent = False
                                student.registration_status = 10
                                student.save()
                        except ConnectionRefusedError as e:
                            is_sms_sent = False
                            student.registration_status = 10
                            student.save()

                else:
                    is_sms_sent = False
                student.registration_status = 11
                student.save()
                current_time = now.strftime("%H:%M:%S")
                data = [student.college.college_code, student.aadhar_number, student.roll_no, 'verification pending',
                        username, password,
                        is_sms_sent,
                        is_email_sent, current_time, email, phone_number]

                writer.writerow(data)
                count = count + 1
                print("pending ", college_students.count() - count)
            except IntegrityError as e:
                student.registration_status = 98  # duplicate username
                student.save()
                print("duplicate username")
        else:
            print("empty roll number")
            student.registration_status = 99  # no number
            student.save()
