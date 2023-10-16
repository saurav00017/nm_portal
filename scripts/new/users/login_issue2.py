import csv
import os
from django.conf import settings
from student.models import Student
from users.models import User, UserDetail

import http.client
import json
import random
file = open(os.path.join(settings.BASE_DIR, "scripts/new/users/student_accounts2.csv"), 'w')
writer = csv.writer(file)

with open(os.path.join(settings.BASE_DIR, "scripts/new/users/student_data.csv")) as f:
    csv_data = csv.reader(f)
    for record in csv_data:
        """
        0 - S No,
        1 Roll No,
        2 Name,
        3 Branch,
        4 Semester,
        5 Email,
        6 Mobile,
        7 Verification Status
        """
        roll_no = str(record[1])
        password = str(random.randint(10000, 99999))
        mobile = None
        try:
            get_student = Student.objects.get(roll_no=roll_no)
            mobile = get_student.phone_number
            get_user_details = UserDetail.objects.get(student_id=get_student.id)
            user_details_count = UserDetail.objects.filter(user_id=get_user_details.user_id).count()
            username = get_user_details.user.username
            new_record = record + ["", "", user_details_count, get_user_details.user_id, get_user_details.user.username]
            if user_details_count > 1:
                try:
                    user_details = UserDetail.objects.get(user_id=get_user_details.user_id, student_id__isnull=True)
                    user_details.delete()
                except:
                    pass
            else:
                get_user_details.user.set_password(password)
                get_user_details.user.save()
                if mobile is not None and username:
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
                    writer.writerow([username, mobile, is_sms_sent] + new_record)

        except UserDetail.DoesNotExist:
            print(record)
            username = ''
            try:
                user = User.objects.get(username="au" + roll_no)
                username = user.username
                get_details = UserDetail.objects.filter(user_id=user.id).exists()
                if get_details:
                    username = "get_details - " + username
                else:
                    new_user_details = UserDetail.objects.create(
                        user_id=user.id,
                        student_id=get_student.id
                    )
                    user.set_password(password)
                    user.save()
            except User.DoesNotExist:
                username = "au" + str(roll_no).strip()
                new_user = User.objects.create(
                    username=username,
                    account_role=8
                )
                new_user.set_password(password)
                new_user.save()
                new_user_details = UserDetail.objects.create(
                    user_id=new_user.id,
                    student_id=get_student.id
                )
            except Exception as e:
                username = ''
            new_record = record + ["", "No UserDetail", username]
            is_sms_sent = None
            if mobile is not None and username:
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
            writer.writerow([username, mobile, is_sms_sent] + new_record)

        except Exception as e:
            username = None
            print("Error ", e)
            new_record =record + [str(e)]
            writer.writerow(["username", 'mobile', "sms sent"]+new_record)
            continue

