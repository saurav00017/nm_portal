import csv
import os
from django.conf import settings
from college.models import College
from student.models import Student
from datetime import datetime
import http.client
import json
import random
from users.models import User
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP

file = open(os.path.join(settings.BASE_DIR, 'scripts/anna_university_spoc_consolidated.csv'))
csv_data = csv.reader(file)

header = ['college_code', 'college_name', 'student_count', 'username', 'password', 'sms_status', 'email_status',
          'timestamp', 'email', 'phone']

file_name = "sept_3_college_dump_" + str(datetime.now().strftime("%H:%M:%S")) + ".csv"
# l
count = 0
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for record in csv_data:
        print(record)
        mobile = record[2].replace(" ", "")
        mobile = int(mobile)
        email = record[3]

        try:
            college_info = College.objects.get(college_code=int(record[0]))
            if college_info.status == 0 or college_info.status == 1:
                college_info.mobile = mobile
                college_info.email = email
                college_info.save()
                username = "tnengg" + str(college_info.college_code)
                username = username.lower()
                password = str(random.randint(100000, 999999))
                try:
                    user_info = User.objects.get(username=username)
                    user_info.set_password(password)
                    user_info.save()
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
                    is_email_sent = True
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
                    except Exception as e:
                        is_sms_sent = False

                data = [college_info.college_code, college_info.college_name,
                        Student.objects.filter(college_id=college_info.id).count(), username,
                        password, is_sms_sent, is_email_sent, str(datetime.now().strftime("%H:%M:%S")), email, mobile]
                writer.writerow(data)
                college_info.status = 1
                college_info.subscription_status = True
                college_info.save()
        except College.DoesNotExist:
            pass
        except College.MultipleObjectsReturned:
            pass
