from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from student.models import Student
from .models import StudentPlacementDetail
from datarepo.models import AccountRole, District, StudentRegistrationStatus, StudentCaste
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


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def student_placement(request):
    account_role = jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])[
        'account_role']
    if account_role == AccountRole.STUDENT:
        user_details = UserDetail.objects.get(user_id=request.user.id)
        if request.method == "GET":
            try:
                placement_details = StudentPlacementDetail.objects.get(student_id=user_details.student_id)
                content = {
                    'student_job_detail_id': placement_details.id,
                    'current_status': placement_details.current_status,
                    'job_offers': placement_details.job_offers,
                    'education_location': placement_details.education_location,
                    'education_location_other': placement_details.education_location_other,
                    'education_degree': placement_details.education_degree,
                    'competitive_exam': placement_details.competitive_exam,
                    'competitive_exam_other': placement_details.competitive_exam_other,
                    'business_sector': placement_details.business_sector,
                    'job_domain': placement_details.job_domain,
                    'job_domain_other': placement_details.job_domain_other,
                    'created': placement_details.created,
                    'updated': placement_details.updated,
                }
                return Response(content, status=status.HTTP_200_OK)
            except StudentPlacementDetail.DoesNotExist:
                return Response({'message': 'Record not found'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'POST':
            try:
                placement_details = StudentPlacementDetail.objects.get(student_id=user_details.student_id)
            except StudentPlacementDetail.DoesNotExist:
                placement_details = StudentPlacementDetail.objects.create(student_id=user_details.student_id)

            current_status = request.POST.get('current_status', None)
            job_offers = request.POST.get('job_offers', None)
            education_location = request.POST.get('education_location', None)
            education_location_other = request.POST.get('education_location_other', None)
            education_degree = request.POST.get('education_degree', None)
            competitive_exam = request.POST.get('competitive_exam', None)
            competitive_exam_other = request.POST.get('competitive_exam_other', None)
            business_sector = request.POST.get('business_sector', None)
            job_domain = request.POST.get('job_domain', None)
            job_domain_other = request.POST.get('job_domain_other', None)
            error = None
            if job_offers:
                try:
                    job_offers = json.loads(job_offers)
                except Exception as e:
                    error = str(e)
                    job_offers = None

            placement_details.current_status = current_status if current_status else ''
            placement_details.job_offers = job_offers if job_offers else ''
            placement_details.education_location = education_location if education_location else ''
            placement_details.education_location_other = education_location_other if education_location_other else ''
            placement_details.education_degree = education_degree if education_degree else ''
            placement_details.competitive_exam = competitive_exam if competitive_exam else ''
            placement_details.competitive_exam_other = competitive_exam_other if competitive_exam_other else ''
            placement_details.business_sector = business_sector if business_sector else ''
            placement_details.job_domain = job_domain if job_domain else ''
            placement_details.job_domain_other = job_domain_other if job_domain_other else ''
            placement_details.save()
            return Response({
                'message': 'updated successfully',
                'placement_details': placement_details.id
            }, status=status.HTTP_200_OK)
    elif account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        if request.method == "GET":
            student_id = request.GET.get('student_id', None)
            if student_id:
                try:
                    placement_details = StudentPlacementDetail.objects.get(student_id=student_id)
                    content = {
                        'student_job_detail_id': placement_details.id,
                        'current_status': placement_details.current_status,
                        'job_offers': placement_details.job_offers,
                        'education_location': placement_details.education_location,
                        'education_location_other': placement_details.education_location_other,
                        'education_degree': placement_details.education_degree,
                        'competitive_exam': placement_details.competitive_exam,
                        'competitive_exam_other': placement_details.competitive_exam_other,
                        'business_sector': placement_details.business_sector,
                        'job_domain': placement_details.job_domain,
                        'job_domain_other': placement_details.job_domain_other,
                        'created': placement_details.created,
                        'updated': placement_details.updated,
                    }
                    return Response(content, status=status.HTTP_200_OK)
                except StudentPlacementDetail.DoesNotExist:
                    return Response({'message': 'Record not found'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'POST':
            student_id = request.POST.get('student_id', None)
            if student_id:
                try:
                    placement_details = StudentPlacementDetail.objects.get(student_id=student_id)
                except StudentPlacementDetail.DoesNotExist:
                    placement_details = StudentPlacementDetail.objects.create(student_id=student_id)

                current_status = request.POST.get('current_status', None)
                job_offers = request.POST.get('job_offers', None)
                education_location = request.POST.get('education_location', None)
                education_location_other = request.POST.get('education_location_other', None)
                education_degree = request.POST.get('education_degree', None)
                competitive_exam = request.POST.get('competitive_exam', None)
                competitive_exam_other = request.POST.get('competitive_exam_other', None)
                business_sector = request.POST.get('business_sector', None)
                job_domain = request.POST.get('job_domain', None)
                job_domain_other = request.POST.get('job_domain_other', None)
                error = None
                if job_offers:
                    try:
                        job_offers = json.loads(job_offers)
                    except Exception as e:
                        error = str(e)
                        job_offers = None

                placement_details.current_status = current_status if current_status else ''
                placement_details.job_offers = job_offers if job_offers else ''
                placement_details.education_location = education_location if education_location else ''
                placement_details.education_location_other = education_location_other if education_location_other else ''
                placement_details.education_degree = education_degree if education_degree else ''
                placement_details.competitive_exam = competitive_exam if competitive_exam else ''
                placement_details.competitive_exam_other = competitive_exam_other if competitive_exam_other else ''
                placement_details.business_sector = business_sector if business_sector else ''
                placement_details.job_domain = job_domain if job_domain else ''
                placement_details.job_domain_other = job_domain_other if job_domain_other else ''
                placement_details.save()
                return Response({
                    'message': 'updated successfully',
                    'placement_details': placement_details.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'You dont have the permission'}, status=status.HTTP_400_BAD_REQUEST)
