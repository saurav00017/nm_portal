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

print("total invites sent - ", Student.objects.filter(registration_status=11, is_mailed=1).count())
print("total student logins - ", Student.objects.filter(payment_status=5).count())
