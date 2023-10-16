from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from ..models import Student, TemporaryFileUpload
from datarepo.models import AccountRole, District, StudentRegistrationStatus, StudentCaste, CollegeType
from users.models import User, UserDetail
from datarepo.models import PaymentStatus
from django.template import Context
from django.db.models import F
from django.template.loader import get_template
from cerberus import Validator
import yaml
import jwt
from django.utils.timezone import datetime, timedelta
import os
from users.views import MyTokenObtainPairSerializer
from nm_portal.config import Config
import json
import razorpay
from college.models import College
RAZORPAY_USERNAME = os.environ.get('RAZORPAY_KEY', '')
RAZORPAY_SECRET_KEY = os.environ.get('RAZORPAY_SECRET_KEY', '')

RAZORPAY_USERNAME="rzp_test_TPNYwIheW2VPhC"
RAZORPAY_SECRET_KEY="Y5mbKfcfdlwludb231FdHhiO"

nm_razorpay_client = razorpay.Client(auth=(RAZORPAY_USERNAME, RAZORPAY_SECRET_KEY))
nm_razorpay_client.set_app_details({"title": "django", "version": "3"})
from datarepo.models import Branch
from .tasks import async_task_confirmation_student_upload_file, async_task_initiate_student_upload_file
# Create your views here.

@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def step_1_upload_file(request):
    """
    # Only access to NM_Admin
    :param request:
    :param college_type:
    :param csv_file:
    :return:
    """
    account_role = \
        jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])['account_role']
    if account_role == AccountRole.NM_ADMIN:
        college_type = request.POST.get('college_type', None)
        csv_file = request.FILES.get('csv_file', None)
        if college_type:
            try:
                college_type = int(college_type)
            except:
                college_type = None
        if college_type is None or csv_file is None:
            return Response({'message': 'Please provide college_type/ csv_file'}, status=status.HTTP_400_BAD_REQUEST)
        csv_data = csv_file.read().decode('utf-8')
        csv_data = str(csv_data).split("\n")
        if len(csv_data) > 1:
            print(type(csv_data))
            new_temporary_file = TemporaryFileUpload.objects.create(
                status=0,
                csv_file_data=csv_data,
                college_type=college_type
            )
            task_initiate = async_task_initiate_student_upload_file.delay(
                temporary_file_id=new_temporary_file.id
            )
            context = {
                "message": "uploaded successfully",
                "temporary_file_id": new_temporary_file.id,
                "data_lines": len(csv_data),
                "data": list(csv_data)
            }
            return Response(context, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'unauthorized'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def step_2_upload_file_list(request):
    """
    # Only access to NM_Admin
    :param request:
    :return:
    """
    account_role = jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])['account_role']
    if account_role == AccountRole.NM_ADMIN:
        page = request.GET.get('page', 0)
        limit = request.GET.get('limit', 20)
        temporary_status = request.GET.get('status', None)
        query = {}
        if temporary_status:
            query['status'] = temporary_status


        try:
            page = 0
            limit = 20
        except:
            page = int(page)
            limit = int(limit)
        temporary_files_list = TemporaryFileUpload.objects.annotate(
            temporary_file_id=F('id')
        ).values(
            'temporary_file_id',
            'status',
            'result_data',
            'college_type',
            'csv_file_data',
            'created',
            'updated',
        ).filter(**query).order_by('-created')[(page*limit): ((page*limit)+ limit)]
        total_count = TemporaryFileUpload.objects.filter(**query).count()
        context = {
            "temporary_files": list(temporary_files_list),
            'page': page,
            'limit': limit,
            'count': total_count,
            'status': temporary_status,
        }
        return Response(context, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'unauthorized'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def step_3_upload_file_celery_initiate(request):
    """
    # Only access to NM_Admin
    :param request:
    :return:
    """
    account_role = \
        jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])['account_role']
    if account_role == AccountRole.NM_ADMIN:
        temporary_file_id = request.GET.get('temporary_file_id', None)
        if temporary_file_id:
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
                    return Response(context, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'already celery task initiate/ completed'}, status=status.HTTP_400_BAD_REQUEST)
            except TemporaryFileUpload.DoesNotExist:
                return Response({'message': 'Please provide valid temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message': 'Please provide temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)


    else:
        return Response({'message': 'unauthorized'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def step_4_upload_file_confirmation(request):
    """
    # Only access to NM_Admin
    :param request:
    :param temporary_file_id:
    :return:
    """
    account_role = \
        jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])['account_role']
    if account_role == AccountRole.NM_ADMIN:
        temporary_file_id = request.POST.get('temporary_file_id', None)
        if temporary_file_id:
            try:
                temporary_file_obj = TemporaryFileUpload.objects.get(id=temporary_file_id)
                if temporary_file_obj.status == 2:
                    confirm_student_upload_file = async_task_confirmation_student_upload_file.delay(
                        temporary_file_id=temporary_file_obj.id
                    )
                    return Response({'message': 'Add to DB initiate'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'already celery task initiate/ completed'}, status=status.HTTP_400_BAD_REQUEST)
            except TemporaryFileUpload.DoesNotExist:
                return Response({'message': 'Please provide valid temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message': 'Please provide temporary_file_id'}, status=status.HTTP_400_BAD_REQUEST)


    else:
        return Response({'message': 'unauthorized'}, status=status.HTTP_400_BAD_REQUEST)
