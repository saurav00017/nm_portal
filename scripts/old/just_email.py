import csv
import uuid
import json
import csv
import sys
import os
import re
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText
from email.utils import formatdate
import time

SMTPserver = 'mail.tn.gov.in'
sender = 'naanmudhalvan@tn.gov.in'
destination = ['pranaymadasi1@gmail.com ','krishnamurthy.tn@gmail.com']

USERNAME = "naanmudhalvan"
PASSWORD = "*nmportal2922*"

# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'
c_username = "username"
c_password = "password"

content = f"""\
        hi, 

first email before real emails





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

subject = "first email before real emails"

msg = MIMEText(content, text_subtype)
msg['Subject'] = subject
msg['From'] = sender  # some SMTP servers will do this automatically, not all
msg['Date'] = formatdate(localtime=True)

conn = SMTP(host=SMTPserver, port=465)
conn.set_debuglevel(False)
conn.login(USERNAME, PASSWORD)
try:
    conn.sendmail(sender, destination, msg.as_string())
finally:
    conn.quit()
