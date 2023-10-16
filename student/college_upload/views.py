from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from ..models import Student, TemporaryFileUpload, CollegeTemporaryFileUpload
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
from .tasks import async_task_initiate_student_upload_by_college
# Create your views here.
import csv


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def step_1_upload_student_csv(request):
    """
    # Only access to NM_Admin
    :param csv_file:
    :return:
    """
    account_role = \
        jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])['account_role']
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            if not user_details.college_id:
                return Response({'message': 'You dont have the permission'}, status=status.HTTP_400_BAD_REQUEST)
            csv_file = request.FILES.get('csv_file', None)
            if csv_file is None:
                return Response({'message': 'Please provide csv_file'}, status=status.HTTP_400_BAD_REQUEST)

            new_college_temporary_file = CollegeTemporaryFileUpload.objects.create(
                status=0,
                csv_file=csv_file,
                college_id=user_details.college_id,
            )
            async_task_initiate_student_upload_by_college.delay(new_college_temporary_file.id)
            context = {
                "message": "uploaded successfully",
                "temporary_file_id": new_college_temporary_file.id,
            }
            return Response(context, status=status.HTTP_200_OK)
        except UserDetail.DoesNotExist:
            return Response({'message': 'You dont have the permission'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'message': 'unauthorized'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def student_bulk_upload_history(request):
    """
    # Only access to NM_Admin
    :param request:
    :return:
    """
    account_role = jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])['account_role']
    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    temporary_status = request.GET.get('status', None)
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF, AccountRole.COLLEGE_ADMIN_STAFF, AccountRole.COLLEGE_ADMIN]:

        query = {}
        if temporary_status:
            query['status'] = temporary_status
        try:
            page = 0
            limit = 20
        except:
            page = int(page)
            limit = int(limit)

        if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['college_id'] = user_details.college_id
        temporary_files_list = CollegeTemporaryFileUpload.objects.annotate(
            temporary_file_id=F('id'),
            college_name=F('college__college_name'),
            college_code=F('college__college_code'),
        ).values(
            'temporary_file_id',
            'status',
            'college_id',
            'college_name',
            'college_code',
            'result_data',
            'created',
            'updated',
        ).filter(**query).order_by('-created')[(page*limit): ((page*limit)+ limit)]
        total_count = CollegeTemporaryFileUpload.objects.filter(**query).count()
        context = {
            "records": list(temporary_files_list),
            'page': page,
            'limit': limit,
            'count': total_count,
            'status': temporary_status,
        }
        return Response(context, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'unauthorized'}, status=status.HTTP_400_BAD_REQUEST)
