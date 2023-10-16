from college.models import College
from student.models import Student
from users.models import UserDetail, User
import random
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText
from email.utils import formatdate
import time

# dont forget about colleg3e type =2


colleges_list = College.objects.filter(status=0,
                                       college_code__in=['280', '1441', '1436', '9537', '1101', '5101', '1501', '1401',
                                                         '6176', '7101', '3128', '7301',
                                                         '7203', '2763', '7302', '1228', '2733', '3803', '9100', '7100',
                                                         '2025', '6202', '1137', '1402',
                                                         '9601', '1133', '224', '2648', '3461', '2103', '8156', '7239',
                                                         '9230', '4944', '5104', '4104',
                                                         '7153', '8207', '3801', '332', '6235', '6201', '2702', '5902',
                                                         '5105', '6203', '7303', '2656',
                                                         '5106', '4952', '4953', '3841', '1321', '4208', '1399', '2630',
                                                         '7104', '7204', '6205', '2007',
                                                         '001', '374', '2105', '4106', '7240', '2743', '3105', '8104',
                                                         '3805', '6105', '9504', '7276',
                                                         '7107', '3822', '4954', '9505', '561', '7205', '9506', '2621',
                                                         '7304', '2667', '7307', '9104',
                                                         '4955', '6206', '5109', '1523', '2624', '1105', '853', '9508',
                                                         '7311', '8301', '3465', '2603',
                                                         '5009', '6135', '2615', '3464', '2005', '115', '122', '146',
                                                         '132', '143', '4931', '2708', '7208',
                                                         '2740', '2373', '8109', '9509', '6211', '8110', '757', '4932',
                                                         '3831', '4976', '105', '569',
                                                         '1126', '8113', '7313', '3807', '7333', '2350', '7111', '2762',
                                                         '3107', '1120', '1201', '9609',
                                                         '2769', '7209', '3108', '2106', '3120', '1307', '7312', '2758',
                                                         '4994', '2606', '7316', '2328',
                                                         '9513', '9107', '8117', '8210', '2607', '9204', '2710', '2735',
                                                         '2745', '3110', '2751', '8211',
                                                         '5113', '9106', '6112', '2653', '591', '2344', '6213', '705',
                                                         '2764', '3410', '4983', '4677',
                                                         '2109', '9612', '8126', '3786', '2608', '4', '3403', '9112',
                                                         '2623', '4216', '5536', '3112',
                                                         '1130', '3857', '4960', '9517', '7339477554', '9114', '3117',
                                                         '3843', '203', '6217', '2314',
                                                         '9209', '9210', '7321', '2639', '9576', '7215', '7210', '7244',
                                                         '4961', '1431', '5832', '8129',
                                                         '3782', '1529', '576', '8212', '2628', '533', '5117', '1209',
                                                         '5912', '1210', '2115', '790',
                                                         '8213', '7123', '2768', '6115', '2657', '3815', '8131', '1452',
                                                         '4966', '9632', '6218', '1525',
                                                         '7236', '7124', '7125', '8215', '1442', '4116', '1414', '5119',
                                                         '505', '2006', '7155', '9523',
                                                         '9524', '4210', '1115', '1112', '1113', '9215', '535', '2117',
                                                         '9619', '202', '7246', '2376',
                                                         '7218', '9525', '9633', '4670', '9214', '1144', '7147', '4967',
                                                         '1114', '5915', '215', '2659',
                                                         '7245', '1449', '9527', '7324', '2122', '9528', '4969', '519',
                                                         '3', '2627', '8216', '2629',
                                                         '6122', '2617', '4917', '333', '6124', '408', '8217', '2120',
                                                         '2734', '7135', '2726', '9122',
                                                         '6178', '1438', '2673', '9218', '4970', '6227', '9126', '3852',
                                                         '2739', '7277', '4121', '387',
                                                         '2126', '2719', '2725', '776', '4125', '4124', '2737', '7327',
                                                         '1315', '885', '1219', '1116',
                                                         '9220', '1422', '2614', '2129', '769', '4221', '3860', '1149',
                                                         '5919', '1317', '8219', '3825',
                                                         '1127', '4971', '9622', '8220', '7211', '3920', '8144', '2360',
                                                         '8155', '7328', '4222', '7221',
                                                         '9128', '578', '4127', '4120', '6230', '7142', '7143', '2728',
                                                         '3126', '109', '1516', '2666',
                                                         '2625', '9222', '9177', '216', '1517', '1518', '1128', '3820',
                                                         '9129', '2761', '9627', '5022',
                                                         '5133', '1026', '5134', '4023', '4226', '8221', '9130', '8222',
                                                         '1013', '3011', '8100', '1014',
                                                         '2', '4024', '9533', '9534', '9225', '9133', '2641', '2723',
                                                         '1132', '1131', '1118', '2633',
                                                         '9226', '9630', '9629', '6129'])
print("total colleges ", colleges_list.count())

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
