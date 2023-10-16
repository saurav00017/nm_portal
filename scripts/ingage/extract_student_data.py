from student.models import Student
import os
import csv
from django.conf import settings
filename = "scripts/ingage/9_stu_engg.csv"

w_file = 'scripts/ingage/final_data.csv'
writer = csv.writer(open(w_file, 'w'))

with open(os.path.join(settings.BASE_DIR, filename), 'r') as file:
    csv_data = csv.reader(file)
    for record in csv_data:
        student_id = None
        #
        # Sl No.,
        # College code,
        # College Name,
        # Registration Number,

        roll_no = record[3]
        try:
            student = Student.objects.get(roll_no__iexact=roll_no)
            writer.writerow([student.invitation_id]+record)
        except:
            writer.writerow([None]+record)
