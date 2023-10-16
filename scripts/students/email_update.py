import json
import os
import csv
from django.conf import settings
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollment, SKillOfferingEnrollmentProgress

file = open(os.path.join(settings.BASE_DIR,
                         'scripts/students/email_update_list.csv'), 'w')
writer = csv.writer(file)

with open(os.path.join(settings.BASE_DIR,
                       'scripts/students/email_list.csv'), 'r') as f:
    csv_data = csv.reader(f)
    writer.writerow(next(csv_data))

    for record in csv_data:
        try:
            student_id = record[0]
            email = record[1]
            student = Student.objects.get(invitation_id=student_id)
            old_email = student.email
            student.email = email
            student.save()
            writer.writerow([student_id, email, old_email])
        except Student.DoesNotExist:
            writer.writerow(record + [None, 'Student not found'])
        except Exception as e:
            writer.writerow(record + [None, str(e)])