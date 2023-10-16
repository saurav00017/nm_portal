from student.models import Student
import csv
from college.models import College
import os.path
import os
from django.conf import settings
from datetime import datetime

final_bulk_students = []
file_name = "scripts/polystudents/college_does_not_exists.csv"
count = 0
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    with open(os.path.join(settings.BASE_DIR, "scripts/polystudents/polystudents_data.csv"), 'r') as file:
        csv_data = csv.reader(file)
        old_college_code = None
        college_id = None
        for record in csv_data:
            count = count + 1
            try:
                college_code = int(record[0])
                #college_code = int(str(record[0])) #new
                roll_no = record[1]
                name = record[2]
                branch_id = int(record[3])
                sem = None
                dob = None
                try:
                    sem = int(record[4])
                except:
                    sem = None
                try:
                    dob = datetime.strptime(record[5], "%d-%m-%Y")
                except:
                    dob = None

                if old_college_code != college_code:
                    old_college_code = college_code
                    try:
                        college = College.objects.values('id').get(college_code=college_code)
                        if college:
                            college_id = college['id']
                    except College.DoesNotExist:
                        print("College Code Does not exit: ", college_code)
                        college_id = None
                        writer.writerow(record)
                if college_id:
                    new_student = Student(
                        payment_status=2,
                        registration_status=4,
                        roll_no=roll_no,
                        sem=sem,
                        rbranch_id=branch_id,
                        dob=dob,
                        aadhar_number=name,
                        college_id=college_id,
                        degree=4,
                        # 28/4/23 added phone_number and email 
                        phone_number = record[6],
                        email = record[7],
                    )
                    final_bulk_students.append(new_student)

            except Exception as e:
                print("Error", e)
            print("Count: ", count)
print("executing bulk")
print(Student.objects.bulk_create(final_bulk_students))
print("complete")
