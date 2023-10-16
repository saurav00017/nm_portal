from celery import shared_task
from ..models import Student, StudentRegistrationStepOne, CollegeTemporaryFileUpload
from datarepo.models import Branch
import csv
from io import StringIO
import uuid
import re
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import Context
from django.conf import settings
from django.template.loader import get_template
from datarepo.models import StudentRegistrationStatus, CollegeType
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from nm_portal.config import Config
import os
import re

@shared_task()
def async_task_initiate_student_upload_by_college(temporary_file_id):
    try:
        temporary_file_obj = CollegeTemporaryFileUpload.objects.get(id=temporary_file_id)
        if temporary_file_obj.status == 0:
            temporary_file_obj.status = 1
            temporary_file_obj.save()
            college = temporary_file_obj.college

            student_invalid_mobile_number = 0
            student_invalid_name = 0
            student_invalid_email = 0
            student_invalid_sem_or_year_of_study = 0

            # - [ ] student_invalid_roll_no_count -
            student_invalid_roll_no_count = 0
            # - [ ] student_invalid_roll_no_data - (student name, roll_no)
            student_invalid_roll_no_data = []
            # - [ ] student_invalid_branch_id_count - counter
            student_invalid_branch_name_count = 0
            # - [ ] student_invalid_branch_id_data - branch_ids list
            student_invalid_branch_name_data = []
            # - [ ] student_failed_records_in_CSV_count - counter
            student_failed_records_in_csv_count = 0
            # - [ ] Student_success_records_in_CSV_count - counter
            student_success_records_in_csv_count = 0

            student_roll_no_already_exists_count = 0
            student_roll_no_already_exists_data = []

            exception_data = []
            final_has_defect = False
            db_student_roll_nos = Student.objects.values_list('roll_no', flat=True)
            with open(os.path.join(settings.BASE_DIR, "media", temporary_file_obj.csv_file.name), 'r') as file:
                csv_data = str(file.read()).split("\n")

                sem_or_year_of_study = None
                print('sem_or_year_of_study',sem_or_year_of_study)
                index = 0
                for row in csv_data:
                    record = row.split(",")
                    index += 1
                    if index == 1:
                        sem_or_year_of_study = record[5]
                        continue
                    print('record', record)

                    # print(type(record), record)
                    """
                    0- Student Name,
                    1- Roll No,
                    2- Mobile,
                    3- Email,
                    4- Branch Name,
                    5- Sem/Year_of_student
                    """
                    try:

                        has_defect = False
                        student_name = record[0]
                        _roll_no = record[1]
                        mobile = record[2]
                        email = record[3]
                        branch_name = record[4]

                        sem = None
                        year_of_study = None
                        if str(sem_or_year_of_study).strip().lower() == "sem":
                            sem = record[5]
                        elif str(sem_or_year_of_study).strip().lower() == "year":
                            year_of_study = record[5]

                        if student_name is not None:
                            student_name = str(student_name).strip()
                        if _roll_no is not None and str(_roll_no).strip() != '':
                            roll_no = str(college.college_code).strip() + str(_roll_no).strip()
                        if mobile is not None:
                            mobile = str(mobile).strip().replace(" ", "")
                        if email is not None:
                            email = str(email).strip().replace(" ", "")
                        if sem is not None:
                            try:
                                sem = int(sem)
                            except:
                                sem = None
                        if year_of_study:
                            year_of_study = str(year_of_study).strip()

                        branch_id = None
                        if branch_name:
                            try:
                                branch = Branch.objects.values('id').get(name__iexact=str(branch_name).strip())
                                branch_id = branch['id']
                            except Exception as e:
                                print("Branch - Error", e)
                                branch_id = None

                        has_defect = False
                    except Exception as e:
                        print("Error - ", record)
                        student_failed_records_in_csv_count += 1
                        exception_data.append({
                            "record": str(record),
                            "exception": str(e)
                        })
                        continue

                    # Sem/ Year check
                    if not (sem or year_of_study):
                        student_invalid_sem_or_year_of_study += 1
                        has_defect = True
                    # Mobile check
                    print("Mobile len", mobile, len(mobile))
                    if not mobile and len(mobile)!=10:
                        has_defect = True
                        student_invalid_mobile_number += 1
                    # Email check
                    regex = "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
                    if not re.fullmatch(regex,email):
                        has_defect = True
                        student_invalid_email += 1
                    # Roll No Check
                    if roll_no == '' or not roll_no:
                        student_invalid_roll_no_count += 1
                        student_invalid_roll_no_data.append({
                            "student_name": student_name,
                            "roll_no": roll_no,
                        })
                        has_defect = True
                    elif roll_no in db_student_roll_nos:
                        student_roll_no_already_exists_count += 1
                        student_roll_no_already_exists_data.append({
                            "student_name": student_name,
                            "roll_no": roll_no,
                        })
                        has_defect = True
                    # branch ID Check
                    if (branch_name == '' or not branch_name) or not branch_id:
                        student_invalid_branch_name_count += 1
                        student_invalid_branch_name_data.append(branch_id)
                        has_defect = True

                    print("Test Case", record)
                    print("roo_no", roll_no, email, branch_id)
                    if has_defect:
                        final_has_defect = True
                        student_failed_records_in_csv_count += 1
                        exception_data.append({
                            "record": str(record),
                            "exception": "has_defect"
                        })
                    else:

                        student_success_records_in_csv_count += 1
                        get_student = Student.objects.create(
                            college_id=college.id,
                            rbranch_id=branch_id,
                            roll_no=roll_no,
                            email=email,
                            phone_number=mobile,
                            sem=sem,
                            year_of_study=year_of_study,
                            aadhar_number=student_name,
                        )
                        get_student.save()

                        print("has_defect", has_defect)

            temporary_file_obj.result_data = {
                "student_invalid_sem_or_year_of_study": student_invalid_sem_or_year_of_study,
                "student_invalid_mobile_number": student_invalid_mobile_number,
                "student_invalid_name": student_invalid_name,
                "student_invalid_email": student_invalid_email,
                "student_invalid_roll_no_count": student_invalid_roll_no_count,
                "student_invalid_roll_no_data": student_invalid_roll_no_data,
                "student_invalid_branch_name_count": student_invalid_branch_name_count,
                "student_invalid_branch_name_data": list(set(student_invalid_branch_name_data)) if student_invalid_branch_name_data else [],
                "student_failed_records_in_csv_count": student_failed_records_in_csv_count,
                "student_success_records_in_csv_count": student_success_records_in_csv_count,
                'student_roll_no_already_exists_count': student_roll_no_already_exists_count,
                'student_roll_no_already_exists_data': student_roll_no_already_exists_data,
                'exception_data': exception_data,
            }
            final_status = 3
            if exception_data or final_has_defect:
                final_status = 4
            temporary_file_obj.status = final_status
            temporary_file_obj.save()
            context = {

                "temporary_file_id": temporary_file_obj.id,
                "status": temporary_file_obj.status,
                "college_type": temporary_file_obj.college_type,
                "result_data": temporary_file_obj.result_data,
                "created": temporary_file_obj.created,
                "updated": temporary_file_obj.updated,
            }
            return context
            # return Response(context, status=status.HTTP_200_OK)
        else:
            return {'message': 'already celery task initiate/ completed'}
            # return Response({'message': 'already celery task initiate/ completed'}, status=status.HTTP_400_BAD_REQUEST)
    except CollegeTemporaryFileUpload.DoesNotExist:
        return {'message': 'Please provide valid temporary_file_id'}
        # return Response({'message': 'Please provide valid temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)

