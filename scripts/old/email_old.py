import csv
from college.models import College
from users.models import User, UserDetail
from datarepo.models import AccountRole
import uuid
import json
import csv
from django.conf import settings

import sys
import os
import re

from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)

# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText


def get_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1]


def get_password_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1][:8]


success_data = []
failed_data = []
file = open(os.path.join(settings.BASE_DIR, 'scripts/nm_colleges.csv'))
csv_data = csv.reader(file)
count = 0
for record in csv_data:

    college_name = record[0]
    college_code = record[1]
    email = record[2]
    print(college_name, email)
    if '@' in str(email) and len(str(college_name))>4:
        username = college_code
        password = get_password_uid()
        new_college = College.objects.create(
            invitation_id=get_uid(),
            status=2,
            college_name=college_name,
            email=email,
            college_code=college_code,
        )

        new_user = User.create_registered_user(
            username=username,
            password=password,
            mobile="0123456789",
            email=email,
            account_role=AccountRole.COLLEGE_ADMIN,
            college_id=new_college.id
        )


        SMTPserver = 'mail.tn.gov.in'
        sender = 'email.tnsdc@tn.gov.in'
        destination = [email]

        USERNAME = "email.tnsdc"
        PASSWORD = "eeHih5ta"

        # typical values for text_subtype are plain, html, xml
        text_subtype = 'plain'
        c_username = username
        c_password = password

        content = f"""\
        Vanakkam,

        Welcome to the massive skilling program for the youth of Tamil Nadu “Naan Mudhalvan”. You are an esteemed partner in this visionary journey. 

        Please click on the link 
        https://naanmudhalvan.tn.gov.in

        With the following credentials
        Username - {c_username} 
        Password - {c_password}

        Thank you for being part of Naan Mudhalvan family.

        Yours truly,
        Naan Mudhalvan Team
        """

        subject = "Invitation to Naan Mudhalvan"

        try:
            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = sender  # some SMTP servers will do this automatically, not all

            conn = SMTP(host=SMTPserver, port=465)
            conn.set_debuglevel(False)
            conn.login(USERNAME, PASSWORD)
            try:
                conn.sendmail(sender, destination, msg.as_string())
            finally:
                conn.quit()
            count = count + 1

        except:
            sys.exit("mail failed; %s" % "CUSTOM_ERROR")  # give an error message

        success_data.append({
            "college_name": college_name,
            "email": email,
            "new_user": new_user.username,
            "password": password,
            "college_id": new_college.id,
        })
    else:
        failed_data.append({
            "college_name": college_name,
            "email": email,
        })

context = {
    "success": success_data,
    "failed": failed_data,
}
print(json.dumps(context))