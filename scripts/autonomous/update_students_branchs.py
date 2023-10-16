import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned

header = ['college_code', 'roll_number', 'branch_name', 'branch_id', 'sem', 'name', 'mobile', 'email', 'status']

file_name = "auto_students_update-3-" + str(datetime.now().strftime("%H:%M:%S")) + ".csv"

file = open(os.path.join(settings.BASE_DIR, 'scripts/autonomous/sheet3.csv'))
csv_data = csv.reader(file)


total_proceed_records = 0
updated_students = 0
college_codes_not_found = []
with open(file_name, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for record in csv_data:
        total_proceed_records = total_proceed_records + 1
        college_code = record[0]
        roll_number = record[1]
        branch_name = record[2]
        sem = record[3]
        name = record[4]
        mobile = record[5]
        email = record[6]
        try:
            student_info = Student.objects.get(college__college_code=college_code, roll_no=roll_number)
            try:
                branch_info = Branch.objects.get(name=record[2].strip())
                student_info.rbranch_id = branch_info.id
                student_info.save()
                updated_students = updated_students + 1
                data = [student_info.college.college_code,
                        student_info.roll_no,
                        branch_info.name,
                        branch_info.id,
                        student_info.sem,
                        student_info.aadhar_number,
                        student_info.phone_number,
                        student_info.email,
                        'updated branch']
                writer.writerow(data)
            except Branch.DoesNotExist:
                branch_info = Branch.objects.create(name=record[2].strip())
                branch_info.save()
                student_info.rbranch_id = branch_info.id
                student_info.save()
                updated_students = updated_students + 1
                data = [student_info.college.college_code,
                        student_info.roll_no,
                        branch_info.name,
                        branch_info.id,
                        student_info.sem,
                        student_info.aadhar_number,
                        student_info.phone_number,
                        student_info.email,
                        'new branch']
                writer.writerow(data)
            except MultipleObjectsReturned:
                branch_info = Branch.objects.filter(name=record[2].strip()).first()
                student_info.rbranch_id = branch_info.id
                student_info.save()
                updated_students = updated_students + 1
                data = [student_info.college.college_code,
                        student_info.roll_no,
                        branch_info.name,
                        branch_info.id,
                        student_info.sem,
                        student_info.aadhar_number,
                        student_info.phone_number,
                        student_info.email,
                        'multiple branch']
                writer.writerow(data)
        except Student.DoesNotExist:
            try:
                college_info = College.objects.get(college_code=college_code)
                new_student = Student.objects.create(
                    payment_status=2,
                    registration_status=4,
                    roll_no=roll_number,
                    sem=sem,
                    aadhar_number=name,
                    college_id=college_info.id,
                    degree=2,
                    phone_number=record[5],
                    email=record[6],
                )
                new_student.save()
                try:
                    branch_info = Branch.objects.get(name=record[2].strip())
                    new_student.rbranch_id = branch_info.id
                    new_student.save()
                    updated_students = updated_students + 1

                    data = [new_student.college.college_code,
                            new_student.roll_no,
                            branch_info.name,
                            branch_info.id,
                            new_student.sem,
                            new_student.aadhar_number,
                            new_student.phone_number,
                            new_student.email,
                            'new record']
                    writer.writerow(data)
                except Branch.DoesNotExist:
                    branch_info = Branch.objects.create(name=record[2].strip())
                    branch_info.save()
                    new_student.rbranch_id = branch_info.id
                    new_student.save()
                    updated_students = updated_students + 1

                    data = [new_student.college.college_code,
                            new_student.roll_no,
                            branch_info.name,
                            branch_info.id,
                            new_student.sem,
                            new_student.aadhar_number,
                            new_student.phone_number,
                            new_student.email,
                            'new record']
                    writer.writerow(data)
                except MultipleObjectsReturned:
                    branch_info = Branch.objects.filter(name=record[2].strip()).first()
                    student_info.rbranch_id = branch_info.id
                    student_info.save()
                    updated_students = updated_students + 1
                    data = [student_info.college.college_code,
                            student_info.roll_no,
                            branch_info.name,
                            branch_info.id,
                            student_info.sem,
                            student_info.aadhar_number,
                            student_info.phone_number,
                            student_info.email,
                            'multiple branch']
                    writer.writerow(data)
            except College.DoesNotExist:
                college_codes_not_found.append(college_code)
                data = [college_code,
                        roll_number,
                        branch_name,
                        'N/A',
                        sem,
                        name,
                        mobile,
                        email,
                        'college not found']
                writer.writerow(data)
        except Exception as e:
            print(e)
            data = [college_code,
                    roll_number,
                    branch_name,
                    'N/A',
                    sem,
                    name,
                    mobile,
                    email,
                    str(e)]
            writer.writerow(data)
        print("Total Proceed Records: ", total_proceed_records)

print("Total Updated Students: ", updated_students)
print("College Codes Not Found: ", college_codes_not_found)
# test
# test
# test
