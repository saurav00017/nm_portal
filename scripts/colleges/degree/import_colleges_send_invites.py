import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from datarepo.models import Branch
from datarepo.models import District
from datarepo.models import AffiliatedUniversity
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
from datarepo.models import AccountRole
import yaml
import jwt
from django.conf import settings
from django.db.models.functions import Lower
from django.db.models import Q
from users.models import User, UserDetail
from student.models import Student
from lms.models import StudentCourse
from django.db import IntegrityError
import random
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP
import http.client
import json
from django.utils.timezone import datetime, timedelta





count = 0
ncount = 0
file = open(os.path.join(settings.BASE_DIR, 'scripts/colleges/degree/30.11.2022.csv'))
csv_data = csv.reader(file)
for record in csv_data:
    affiliated_university = record[1].strip().upper()
    college_code = str(record[0]).strip().lower() + str(record[2]).strip().lower()
    management_type = record[3]
    district = record[4].strip().upper()
    pincode = None if record[5].strip() == '' else int(record[5].strip().lower().replace(' ','').replace('.','').replace(',',''))
    spoc_name = record[6].strip()
    spoc_email = record[7].strip().lower()
    spoc_phone = record[8].strip()
    college_name = record[9].strip()
    address = record[10].strip()
    affiliated_university_obj = None
    college_category_id = None
    if management_type == '1':
        college_category_id = 3
    elif management_type == '2':
        college_category_id = 14
    elif management_type == '9':
        college_category_id = 17
    elif management_type == '10':
        college_category_id = 5
    elif management_type == '11':
        college_category_id = 15
    elif management_type == '12':
        college_category_id = 18
    elif management_type == '13':
        college_category_id = 19
    elif management_type == '14':
        college_category_id = 20
    
    try:
        affiliated_university_obj = AffiliatedUniversity.objects.get(name=affiliated_university)
    except AffiliatedUniversity.DoesNotExist:
        affiliated_university_obj = AffiliatedUniversity.objects.create(name=affiliated_university)
    district_obj = None
    try:
        district_obj = District.objects.get(name=district)
    except District.DoesNotExist:
        district_obj = District.objects.create(name=district)
    try:
        new_college = College.objects.get(college_code=college_code)
        new_college.affiliated_university_id = affiliated_university_obj.id
        new_college.management_type = management_type
        new_college.district_id = district_obj.id
        new_college.pincode = pincode
        new_college.college_name = college_name
        new_college.address = address
        new_college.status = 0
        new_college.email = spoc_email
        new_college.mobile = spoc_phone
        new_college.spoc_name = spoc_name
        new_college.college_type = 1
        new_college.college_category_id = college_category_id
        new_college.save()
        count = count + 1
        print("current count ",(count+ncount))
        print("college_name ",new_college.college_name)
        username = ''
                    #
        if new_college.college_type == 2:
            # Engineering
            username = 'tnengg' + str(new_college.college_code)
        elif new_college.college_type == 1:
            # Arts & Science
            username = 'tnas' + str(new_college.college_code)
        elif new_college.college_type == 4:
            username = 'tnpoly0' + str(new_college.college_code)
        username = username.lower()
        password = str(random.randint(100000, 999999))
        error_message = None
        try:
            user_info = User.objects.get(username=username)
            user_info.set_password(password)
            user_info.save()
            print("user updated")
        except User.DoesNotExist:
            new_user = User.create_registered_user(
                username=username,
                college_id=new_college.id,
                password=password,
                account_role=6,
                email='',
                mobile='',
            )
            new_user.save()
            print("user created")
        """
        """
        SMTPserver = settings.CUSTOM_SMTP_HOST
        sender = settings.CUSTOM_SMTP_SENDER

        USERNAME = settings.CUSTOM_SMTP_USERNAME
        PASSWORD = settings.CUSTOM_SMTP_PASSWORD

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
            conn.sendmail(sender, [new_college.email], msg.as_string())
            is_email_sent = True
        except Exception as e:
            print("\n\n\nSEND MAIL\n\n\n",str(e), "\n\n\n")
            is_email_sent = False
        finally:
            conn.quit()
        is_sms_sent = None
        if new_college.mobile is not None:
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
                            "MSISDN": "91" + str(new_college.mobile),
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
                """
                
                """
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
                print("\n\n\nSEND SMS\n\n\n",str(e), "\n\n\n")
                is_sms_sent = False
        if is_sms_sent:
            print("sms sent")
            new_college.status = 1
            new_college.save()
        if is_email_sent:
            print("email sent")
        print("====================================")
    except College.DoesNotExist:
        new_college = College.objects.create(
            college_code=college_code,
            affiliated_university_id = affiliated_university_obj.id,
            management_type = management_type,
            district_id = district_obj.id,
            pincode = pincode,
            college_name = college_name,
            address = address,
            status = 0,
            email = spoc_email,
            mobile = spoc_phone,
            spoc_name = spoc_name,
            college_type = 1,
            college_category_id = college_category_id,
            )
        new_college.save()
        ncount = ncount + 1
        print("current count " ,(count+ncount))
        print("college_name",new_college.college_name)
        username = ''
                    #
        if new_college.college_type == 2:
            # Engineering
            username = 'tnengg' + str(new_college.college_code)
        elif new_college.college_type == 1:
            # Arts & Science
            username = 'tnas' + str(new_college.college_code)
        elif new_college.college_type == 4:
            username = 'tnpoly0' + str(new_college.college_code)
        username = username.lower()
        password = str(random.randint(100000, 999999))
        error_message = None
        try:
            user_info = User.objects.get(username=username)
            user_info.set_password(password)
            user_info.save()
        except User.DoesNotExist:
            new_user = User.create_registered_user(
                username=username,
                college_id=new_college.id,
                password=password,
                account_role=6,
                email='',
                mobile='',
            )
            new_user.save()
        """
        """
        SMTPserver = settings.CUSTOM_SMTP_HOST
        sender = settings.CUSTOM_SMTP_SENDER

        USERNAME = settings.CUSTOM_SMTP_USERNAME
        PASSWORD = settings.CUSTOM_SMTP_PASSWORD

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
            conn.sendmail(sender, [new_college.email], msg.as_string())
            is_email_sent = True
        except Exception as e:
            print("\n\n\nSEND MAIL\n\n\n",str(e), "\n\n\n")
            is_email_sent = False
        finally:
            conn.quit()
        is_sms_sent = None
        if new_college.mobile is not None:
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
                            "MSISDN": "91" + str(new_college.mobile),
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
                print("\n\n\nSEND SMS\n\n\n",str(e), "\n\n\n")
                is_sms_sent = False
        if is_sms_sent:
            print("sms sent")
            new_college.status = 1
            new_college.save()
        if is_email_sent:
            print("email sent")
        print("====================================")
print("updated ", count)
print("new ",ncount)