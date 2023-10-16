from celery import shared_task
from college.models import College
from ..models import Student, StudentRegistrationStepOne, TemporaryFileUpload
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
from datarepo.models import StudentRegistrationStatus
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from nm_portal.config import Config


@shared_task()
def async_task_confirmation_student_upload_file(temporary_file_id):
    try:
        temporary_file_obj = TemporaryFileUpload.objects.get(id=temporary_file_id)
        if temporary_file_obj.status == 2:
            temporary_file_obj.status = 3
            temporary_file_obj.save()

            # - [ ] student_non_college_codes - counter of students
            student_non_college_codes = 0
            # - [ ] Student_invalid_college_codes_data - list of data of college code
            student_invalid_college_codes_data = []
            # - [ ] student_invalid_college_codes_count - counter of students
            student_invalid_college_codes_count = 0
            # - [ ] student_invalid_roll_no_count -
            student_invalid_roll_no_count = 0
            # - [ ] student_invalid_roll_no_data - (student name, roll_no)
            student_invalid_roll_no_data = []
            # - [ ] student_invalid_branch_id_count - counter
            student_invalid_branch_id_count = 0
            # - [ ] student_invalid_branch_id_data - branch_ids list
            student_invalid_branch_id_data = []
            # - [ ] student_failed_records_in_CSV_count - counter
            student_failed_records_in_csv_count = 0
            # - [ ] Student_success_records_in_CSV_count - counter
            student_success_records_in_csv_count = 0

            student_roll_no_already_exists_count = 0
            student_roll_no_already_exists_data = []

            db_college_codes = College.objects.values_list('college_code', flat=True)
            db_student_roll_nos = Student.objects.values_list('roll_no', flat=True)
            db_branch_ids = Branch.objects.values_list('id', flat=True)
            for record in temporary_file_obj.csv_file_data[1:]:
                record = str(record).split(",")
                # print(type(record), record)
                """
                0 - College Code,
                1- Student Name,
                2- Roll No,
                3- phone_number,
                4- Email,
                5- Branch ID,
                6- Sem"
                """
                college_code = record[0]
                if college_code is not None:
                    college_code = str(college_code).strip()
                student_name = record[1]
                if student_name is not None:
                    student_name = str(student_name).strip()
                roll_no = record[2]
                if roll_no is not None:
                    roll_no = str(roll_no).strip().replace(" ", "")
                phone_number = record[3]
                email = record[4]
                branch_id = record[5]
                if branch_id is not None:
                    branch_id = str(branch_id).strip()
                sem = record[6]
                if sem is not None:
                    try:
                        sem = int(sem)
                    except:
                        sem = None
                has_defect = False
                print(college_code, roll_no)
                # College Code Check
                if college_code == '' or not college_code:
                    student_non_college_codes += 1
                    student_invalid_college_codes_data.append(college_code)
                    has_defect = True
                elif college_code not in db_college_codes:
                    student_invalid_college_codes_data.append(college_code)
                    student_invalid_college_codes_count += 1
                    has_defect = True

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
                if branch_id == '' or not branch_id:
                    student_invalid_branch_id_count += 1
                    student_invalid_branch_id_data.append(branch_id)
                    has_defect = True
                else:
                    try:
                        int_branch_id = int(branch_id)
                        if int_branch_id not in db_branch_ids:
                            student_invalid_branch_id_count += 1
                            student_invalid_branch_id_data.append(branch_id)
                            has_defect = True
                    except:
                        student_invalid_branch_id_count += 1
                        student_invalid_branch_id_data.append(branch_id)
                        has_defect = True

                if has_defect:
                    student_failed_records_in_csv_count += 1
                else:
                    student_success_records_in_csv_count += 1
                    try:
                        college_obj = College.objects.values('id').get(college_code=college_code)
                        try:
                            get_student = Student.objects.get(roll_no=roll_no)
                            get_student.college_id = college_obj['id']
                            get_student.rbranch_id = branch_id
                            get_student.email = email
                            get_student.phone_number = phone_number
                            get_student.sem = sem
                            get_student.aadhar_number = student_name
                            get_student.save()
                        except Student.MultipleObjectsReturned:
                            get_students = Student.objects.filter(roll_no=roll_no)
                            for _student in get_students:
                                _student.college_id = college_obj['id']
                                _student.rbranch_id = branch_id
                                _student.email = email
                                _student.phone_number = phone_number
                                _student.sem = sem
                                _student.aadhar_number = student_name
                                _student.save()
                        except Student.DoesNotExist:
                            try:
                                get_student = Student.objects.create(
                                    college_id=college_obj['id'],
                                    rbranch_id=branch_id,
                                    roll_no=roll_no,
                                    email=email,
                                    phone_number=phone_number,
                                    sem=sem,
                                    aadhar_number=student_name
                                )
                                get_student.save()
                            except Exception as e:
                                print("Error -> ", e)
                    except College.DoesNotExist:
                        student_failed_records_in_csv_count += 1
            temporary_file_obj.result_data = {
                "student_non_college_codes": student_non_college_codes,
                "student_invalid_college_codes_data": list(set(student_invalid_college_codes_data)) if student_invalid_college_codes_data else [],
                "student_invalid_college_codes_count": student_invalid_college_codes_count,
                "student_invalid_roll_no_count": student_invalid_roll_no_count,
                "student_invalid_roll_no_data": student_invalid_roll_no_data,
                "student_invalid_branch_id_count": student_invalid_branch_id_count,
                "student_invalid_branch_id_data": list(set(student_invalid_branch_id_data)) if student_invalid_branch_id_data else [],
                "student_failed_records_in_csv_count": student_failed_records_in_csv_count,
                "student_success_records_in_csv_count": student_success_records_in_csv_count,
                'student_roll_no_already_exists_count': student_roll_no_already_exists_count,
                'student_roll_no_already_exists_data': student_roll_no_already_exists_data
            }
            temporary_file_obj.status = 4
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
    except TemporaryFileUpload.DoesNotExist:
        return {'message': 'Please provide valid temporary_file_id', 'temporary_file_id': temporary_file_id}
        # return Response({'message': 'Please provide valid temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)


@shared_task()
def async_task_initiate_student_upload_file(temporary_file_id):
    try:
        temporary_file_obj = TemporaryFileUpload.objects.get(id=temporary_file_id)
        if temporary_file_obj.status == 0:
            temporary_file_obj.status = 1
            temporary_file_obj.save()

            # - [ ] student_non_college_codes - counter of students
            student_non_college_codes = 0
            # - [ ] Student_invalid_college_codes_data - list of data of college code
            student_invalid_college_codes_data = []
            # - [ ] student_invalid_college_codes_count - counter of students
            student_invalid_college_codes_count = 0
            # - [ ] student_invalid_roll_no_count -
            student_invalid_roll_no_count = 0
            # - [ ] student_invalid_roll_no_data - (student name, roll_no)
            student_invalid_roll_no_data = []
            # - [ ] student_invalid_branch_id_count - counter
            student_invalid_branch_id_count = 0
            # - [ ] student_invalid_branch_id_data - branch_ids list
            student_invalid_branch_id_data = []
            # - [ ] student_failed_records_in_CSV_count - counter
            student_failed_records_in_csv_count = 0
            # - [ ] Student_success_records_in_CSV_count - counter
            student_success_records_in_csv_count = 0

            student_roll_no_already_exists_count = 0
            student_roll_no_already_exists_data = []

            exception_data = []
            db_college_codes = College.objects.values_list('college_code', flat=True)
            db_student_roll_nos = Student.objects.values_list('roll_no', flat=True)
            db_branch_ids = Branch.objects.values_list('id', flat=True)
            for record in temporary_file_obj.csv_file_data[1:]:

                record = str(record).split(",")
                # print(type(record), record)
                """
                0 - College Code,
                1- Student Name,
                2- Roll No,
                3- Mobile,
                4- Email,
                5- Branch ID,
                6- Sem"
                """
                try:
                    college_code = record[0]
                    if college_code is not None:
                        college_code = str(college_code).strip()
                    student_name = record[1]
                    if student_name is not None:
                        student_name = str(student_name).strip()
                    roll_no = record[2]
                    if roll_no is not None:
                        roll_no = str(roll_no).strip().replace(" ", "")
                    mobile = record[3]
                    email = record[4]
                    branch_id = record[5]
                    if branch_id is not None:
                        branch_id = str(branch_id).strip()
                    sem = record[6]
                    has_defect = False
                except Exception as e:
                    print("Error - ", record)
                    student_failed_records_in_csv_count += 1
                    exception_data.append({
                        "record": str(record),
                        "exception": str(e)
                    })
                    continue

                print(college_code, roll_no)
                # College Code Check
                if college_code == '' or not college_code:
                    student_non_college_codes += 1
                    student_invalid_college_codes_data.append(college_code)
                    has_defect = True
                elif college_code not in db_college_codes:
                    student_invalid_college_codes_data.append(college_code)
                    student_invalid_college_codes_count += 1
                    has_defect = True

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
                if branch_id == '' or not branch_id:
                    student_invalid_branch_id_count += 1
                    student_invalid_branch_id_data.append(branch_id)
                    has_defect = True
                else:
                    try:
                        int_branch_id = int(branch_id)
                        if int_branch_id not in db_branch_ids:
                            student_invalid_branch_id_count += 1
                            student_invalid_branch_id_data.append(branch_id)
                            has_defect = True
                    except:
                        student_invalid_branch_id_count += 1
                        student_invalid_branch_id_data.append(branch_id)
                        has_defect = True

                if has_defect:
                    student_failed_records_in_csv_count += 1
                else:
                    student_success_records_in_csv_count += 1

            temporary_file_obj.result_data = {
                "student_non_college_codes": student_non_college_codes,
                "student_invalid_college_codes_data": list(set(student_invalid_college_codes_data)) if student_invalid_college_codes_data else [],
                "student_invalid_college_codes_count": student_invalid_college_codes_count,
                "student_invalid_roll_no_count": student_invalid_roll_no_count,
                "student_invalid_roll_no_data": student_invalid_roll_no_data,
                "student_invalid_branch_id_count": student_invalid_branch_id_count,
                "student_invalid_branch_id_data": list(set(student_invalid_branch_id_data)) if student_invalid_branch_id_data else [],
                "student_failed_records_in_csv_count": student_failed_records_in_csv_count,
                "student_success_records_in_csv_count": student_success_records_in_csv_count,
                'student_roll_no_already_exists_count': student_roll_no_already_exists_count,
                'student_roll_no_already_exists_data': student_roll_no_already_exists_data,
                'exception_data': exception_data,
            }
            temporary_file_obj.status = 2
            temporary_file_obj.save()
            context = {

                "temporary_file_id": temporary_file_obj.id,
                "status": temporary_file_obj.status,
                "college_type": temporary_file_obj.college_type,
                "csv_file_data": temporary_file_obj.csv_file_data,
                "result_data": temporary_file_obj.result_data,
                "created": temporary_file_obj.created,
                "updated": temporary_file_obj.updated,
            }
            return context
            # return Response(context, status=status.HTTP_200_OK)
        else:
            return {'message': 'already celery task initiate/ completed'}
            # return Response({'message': 'already celery task initiate/ completed'}, status=status.HTTP_400_BAD_REQUEST)
    except TemporaryFileUpload.DoesNotExist:
        return {'message': 'Please provide valid temporary_file_id'}
        # return Response({'message': 'Please provide valid temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)


@shared_task()
def async_task_initiate_student_upload_by_college(temporary_file_id):
    try:
        temporary_file_obj = TemporaryFileUpload.objects.get(id=temporary_file_id)
        if temporary_file_obj.status == 0:
            temporary_file_obj.status = 1
            temporary_file_obj.save()

            # - [ ] student_non_college_codes - counter of students
            student_non_college_codes = 0
            # - [ ] Student_invalid_college_codes_data - list of data of college code
            student_invalid_college_codes_data = []
            # - [ ] student_invalid_college_codes_count - counter of students
            student_invalid_college_codes_count = 0
            # - [ ] student_invalid_roll_no_count -
            student_invalid_roll_no_count = 0
            # - [ ] student_invalid_roll_no_data - (student name, roll_no)
            student_invalid_roll_no_data = []
            # - [ ] student_invalid_branch_id_count - counter
            student_invalid_branch_id_count = 0
            # - [ ] student_invalid_branch_id_data - branch_ids list
            student_invalid_branch_id_data = []
            # - [ ] student_failed_records_in_CSV_count - counter
            student_failed_records_in_csv_count = 0
            # - [ ] Student_success_records_in_CSV_count - counter
            student_success_records_in_csv_count = 0

            student_roll_no_already_exists_count = 0
            student_roll_no_already_exists_data = []

            exception_data = []
            db_college_codes = College.objects.values_list('college_code', flat=True)
            db_student_roll_nos = Student.objects.values_list('roll_no', flat=True)
            db_branch_ids = Branch.objects.values_list('id', flat=True)
            for record in temporary_file_obj.csv_file_data[1:]:

                record = str(record).split(",")
                # print(type(record), record)
                """
                0 - College Code,
                1- Student Name,
                2- Roll No,
                3- Mobile,
                4- Email,
                5- Branch ID,
                6- Sem"
                """
                try:
                    college_code = record[0]
                    if college_code is not None:
                        college_code = str(college_code).strip()
                    student_name = record[1]
                    if student_name is not None:
                        student_name = str(student_name).strip()
                    roll_no = record[2]
                    if roll_no is not None:
                        roll_no = str(roll_no).strip().replace(" ", "")
                    mobile = record[3]
                    email = record[4]
                    branch_id = record[5]
                    if branch_id is not None:
                        branch_id = str(branch_id).strip()
                    sem = record[6]
                    has_defect = False
                except Exception as e:
                    print("Error - ", record)
                    student_failed_records_in_csv_count += 1
                    exception_data.append({
                        "record": str(record),
                        "exception": str(e)
                    })
                    continue

                print(college_code, roll_no)
                # College Code Check
                if college_code == '' or not college_code:
                    student_non_college_codes += 1
                    student_invalid_college_codes_data.append(college_code)
                    has_defect = True
                elif college_code not in db_college_codes:
                    student_invalid_college_codes_data.append(college_code)
                    student_invalid_college_codes_count += 1
                    has_defect = True

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
                if branch_id == '' or not branch_id:
                    student_invalid_branch_id_count += 1
                    student_invalid_branch_id_data.append(branch_id)
                    has_defect = True
                else:
                    try:
                        int_branch_id = int(branch_id)
                        if int_branch_id not in db_branch_ids:
                            student_invalid_branch_id_count += 1
                            student_invalid_branch_id_data.append(branch_id)
                            has_defect = True
                    except:
                        student_invalid_branch_id_count += 1
                        student_invalid_branch_id_data.append(branch_id)
                        has_defect = True

                if has_defect:
                    student_failed_records_in_csv_count += 1
                else:
                    student_success_records_in_csv_count += 1

            temporary_file_obj.result_data = {
                "student_non_college_codes": student_non_college_codes,
                "student_invalid_college_codes_data": list(set(student_invalid_college_codes_data)) if student_invalid_college_codes_data else [],
                "student_invalid_college_codes_count": student_invalid_college_codes_count,
                "student_invalid_roll_no_count": student_invalid_roll_no_count,
                "student_invalid_roll_no_data": student_invalid_roll_no_data,
                "student_invalid_branch_id_count": student_invalid_branch_id_count,
                "student_invalid_branch_id_data": list(set(student_invalid_branch_id_data)) if student_invalid_branch_id_data else [],
                "student_failed_records_in_csv_count": student_failed_records_in_csv_count,
                "student_success_records_in_csv_count": student_success_records_in_csv_count,
                'student_roll_no_already_exists_count': student_roll_no_already_exists_count,
                'student_roll_no_already_exists_data': student_roll_no_already_exists_data,
                'exception_data': exception_data,
            }
            temporary_file_obj.status = 2
            temporary_file_obj.save()
            context = {

                "temporary_file_id": temporary_file_obj.id,
                "status": temporary_file_obj.status,
                "college_type": temporary_file_obj.college_type,
                "csv_file_data": temporary_file_obj.csv_file_data,
                "result_data": temporary_file_obj.result_data,
                "created": temporary_file_obj.created,
                "updated": temporary_file_obj.updated,
            }
            return context
            # return Response(context, status=status.HTTP_200_OK)
        else:
            return {'message': 'already celery task initiate/ completed'}
            # return Response({'message': 'already celery task initiate/ completed'}, status=status.HTTP_400_BAD_REQUEST)
    except TemporaryFileUpload.DoesNotExist:
        return {'message': 'Please provide valid temporary_file_id'}
        # return Response({'message': 'Please provide valid temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)

