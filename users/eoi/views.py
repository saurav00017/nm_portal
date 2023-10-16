from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
import yaml
from ..models import User, UserDetail, EOIDetail, EOIRegistration
from datarepo.models import AccountRole
from datarepo.models import PaymentStatus, StudentRegistrationStatus
from college.models import CollegeSubscription, CollegeStatus
from student.models import Student, StudentPaymentDetail
from django.conf import settings
from django.utils.timezone import datetime, timedelta
import os
import razorpay
from nm_portal.config import Config
from college.models import College
from student.models import Student

from django.conf import settings
from django.template.loader import get_template
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives

from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP

from nm_portal.config import Config
from kp.models import KnowledgePartner
from django.utils import timezone
import random
import jwt
import uuid
import json
import socket
from .task import async_scp_with_eoi_files
# latest
import io
import xlsxwriter
import http
SMTPserver = 'mail.tn.gov.in'
sender = 'naanmudhalvan@tn.gov.in'

USERNAME = "naanmudhalvan"
PASSWORD = "*nmportal2922*"
from django.http import HttpResponse
import csv

@api_view(['POST'])
def eoi_otp(request):
    mobile_number = request.POST.get('mobile_number', None)

    if mobile_number and len(str(mobile_number).strip()) >= 10:
        try:
            try:
                eoi_registration = EOIRegistration.objects.get(mobile_number=str(mobile_number).strip())
            except EOIRegistration.DoesNotExist:
                check_username = True
                user = None
                while check_username:
                    uid = str(uuid.uuid4()).replace("-", "")[::-1]
                    new_username = "eoi_" + str(uid)[:8]
                    check_user = User.objects.filter(username__iexact=new_username).exists()
                    if not check_user:
                        user = User.objects.create(
                            username=new_username,
                            account_role=AccountRole.EOI_USER
                        )
                        check_username = False

                eoi_registration = EOIRegistration.objects.create(
                    user_id=user.id,
                    mobile_number=str(mobile_number).strip())
                # eoi_details = EOIDetail.objects.create(user_id=user.id)

            # OTP Request Count Level check
            if eoi_registration.verification_expiry:
                if eoi_registration.verification_request_count >= 3:
                    # verification_expiry already added 90 seconds from time of OTP generated
                    if timezone.now() < eoi_registration.verification_expiry + timedelta(minutes=28, seconds=30):
                        content = {
                            'message': "OTP request limit exceed. Please try again after 30 minutes",
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        eoi_registration.verification_request_count = 0

            # OTP Attempt Count Level check
            if eoi_registration.verification_attempt and eoi_registration.verification_expiry:
                # verification_expiry already added 90 seconds from time of OTP generated
                if eoi_registration.verification_attempt >= 3 and timezone.now() < eoi_registration.verification_expiry + timedelta(minutes=28, seconds=30):
                    content = {
                        'message': "OTP attempts limit exceed. Please try again after 30 minutes",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            try:
                # SMS Code
                verification_code = random.randint(10000, 99999)
                eoi_registration.verification_code = verification_code
                is_sms_sent = False
                try:
                    conn = http.client.HTTPConnection("digimate.airtel.in:15181")
                    payload = json.dumps({
                        "keyword": "DEMO",
                        "timeStamp": "1659688504",
                        "dataSet": [
                            {
                                "UNIQUE_ID": "16596885049652",
                                "MESSAGE": str(verification_code) + " is your OTP for Naan Mudhalvan verification. Do not share your OTP to anyone.NMGOVT",
                                "OA": "NMGOVT",
                                "MSISDN": "91" + str(mobile_number),
                                "CHANNEL": "SMS",
                                "CAMPAIGN_NAME": "tnega_u",
                                "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                "USER_NAME": "tnega_tnsd",
                                "DLT_TM_ID": "1001096933494158",
                                "DLT_CT_ID": "1007549313539937051",
                                "DLT_PE_ID": "1001857722001387178"
                            }
                        ]
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    conn.request("GET", "/BULK_API/InstantJsonPush", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    sms_response = data.decode("utf-8")
                    if sms_response == 'true':
                        is_sms_sent = True
                        eoi_registration.verification_expiry = timezone.now() + timedelta(seconds=90)
                        eoi_registration.verification_attempt = None
                        eoi_registration.verification_request_count += 1
                        eoi_registration.save()
                        content = {
                            'message': "Verification code send your mobile number",
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                    else:
                        is_sms_sent = False
                        content = {
                            'message': "Please try again later",
                            "data": data
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except ConnectionRefusedError:
                    is_sms_sent = False
                    content = {
                        'message': "Please try again later",
                        "error": 'ConnectionRefusedError'
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            except Exception as e:
                # print(e)
                content = {
                    'message': "Please try again later",
                    "error": str(e)
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except Exception as e:
            # print(e)
            content = {
                'message': "Please provide valid email/ password",
                "error": str(e)
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "invalid mobile_number",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['account_role'] = user.account_role if user else None
        return token


@api_view(['POST'])
def eoi_otp_verification(request):
    mobile_number = request.POST.get('mobile_number', None)
    verification_code = request.POST.get('verification_code', None)
    try:
        verification_code = int(verification_code)
    except:
        verification_code = 'invalid'
    if mobile_number and verification_code:

        try:
            eoi_registration = EOIRegistration.objects.get(mobile_number=mobile_number)

            if eoi_registration.verification_attempt and eoi_registration.verification_expiry:
                # verification_expiry already added 90 seconds from time of OTP generated
                if eoi_registration.verification_attempt >= 3 and timezone.now() < eoi_registration.verification_expiry + timedelta(minutes=28, seconds=30):
                    content = {
                        'message': "OTP attempts limit exceed. Please try again after 30 minutes",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if not eoi_registration.verification_expiry:
                content = {
                    'message': "Please request the OTP",
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')
            if eoi_registration.verification_expiry >= timezone.now():
                if eoi_registration.verification_code != verification_code:
                    if eoi_registration.verification_attempt:
                        eoi_registration.verification_attempt += 1
                    else:
                        eoi_registration.verification_attempt = 1
                    eoi_registration.save()
                    if eoi_registration.verification_attempt >= 3:
                        error_message = "OTP attempts limit exceed. Please try again after 30 minutes"
                    else:
                        error_message = "Invalid OTP"
                    content = {
                        'message': error_message,
                        "attempt_count": eoi_registration.verification_attempt
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                eoi_registration.verification_code = None
                eoi_registration.verification_attempt = None
                eoi_registration.save()

                refresh_token = MyTokenObtainPairSerializer.get_token(user=eoi_registration.user)
                # print(user.account_role)
                content = {
                    "mobile_number": eoi_registration.mobile_number,
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token)
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            else:
                content = {
                    'message': "verification code has been expired",
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

        except EOIRegistration.DoesNotExist:
            content = {
                'message': "Please provide valid mobile_number/ verification code",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


    else:
        content = {
            'message': "Please provide mobile_number/ verification code",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def eoi_details_v2(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role == AccountRole.EOI_USER:
        try:
            if request.method == 'GET':

                page = request.GET.get('page', 0)
                limit = request.GET.get('limit', 20)
                try:
                    page = int(page)
                    limit = int(limit)
                except:
                    page = 0
                    limit = 20
                eoi_records = EOIDetail.objects.filter(user_id=request.user.id)
                content = {
                    "eoi_list": [{
                        'eoi_detail_id': eoi.id,
                        'status': eoi.status,
                        'organisation_name': eoi.organisation_name,
                        'contact_person_name': eoi.contact_person_name,
                        'email': eoi.email,
                        'sectors': eoi.sectors,
                        'specialization': eoi.specialization,
                        'details_submitted_on': eoi.details_submitted_on,
                        'registration_document': eoi.registration_document.url if eoi.registration_document else None,
                        'declaration_document': eoi.declaration_document.url if eoi.declaration_document else None,
                        'detailed_proposal_document': eoi.detailed_proposal_document.url if eoi.detailed_proposal_document else None,
                        'cost_per_student': eoi.cost_per_student,
                        'mode': eoi.mode,
                        'created': eoi.created,
                        'updated': eoi.updated, } for eoi in eoi_records[(page * limit): ((page * limit) + limit)]],
                    "total_count": eoi_records.count() if eoi_records else 0,
                    'page': page,
                    'limit': limit

                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            elif request.method == 'POST':
                organisation_name = request.POST.get('organisation_name', None)
                registration_document = request.FILES.get('registration_document', None)
                detailed_proposal_document = request.FILES.get('detailed_proposal_document', None)
                declaration_document = request.FILES.get('declaration_document', None)
                contact_person_name = request.POST.get('contact_person_name', None)
                mobile_number = request.POST.get('mobile_number', None)
                email = request.POST.get('email', None)
                sectors = request.POST.get('sectors', None)
                mode = request.POST.get('mode', None)
                cost_per_student = request.POST.get('cost_per_student', None)
                specialization = request.POST.get('specialization', None)
                if not organisation_name or not registration_document or not registration_document or \
                        not contact_person_name or not mobile_number or not email or \
                        not sectors or not specialization or not detailed_proposal_document or not declaration_document:

                    content = {
                        "message": "Please provide "
                                   "organisation_name/ "
                                   "registration_document/ "
                                   "contact_person_name/ "
                                   "mobile_number/ "
                                   "email/ "
                                   "sectors/ "
                                   "specialization/ "
                                   "detailed_proposal_document/ "
                                   "declaration_document"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                # if eoi.status == 1:
                #     content = {
                #         "message": "Details already submitted",
                #     }
                #     return Response(content, status.HTTP_200_OK, content_type='application/json')
                eoi = EOIDetail.objects.create(user_id=request.user.id)

                eoi.organisation_name = organisation_name
                eoi.registration_document = registration_document
                eoi.contact_person_name = contact_person_name
                eoi.mobile_number = mobile_number
                eoi.email = email
                eoi.sectors = sectors
                eoi.cost_per_student = cost_per_student
                eoi.mode = mode
                eoi.specialization = specialization
                eoi.detailed_proposal_document = detailed_proposal_document
                eoi.declaration_document = declaration_document
                eoi.details_submitted_on = timezone.now()
                eoi.status = 1
                eoi.save()

                task = async_scp_with_eoi_files.delay(eoi.id)

                content = {
                    "message": "updated successfully",
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

        except EOIDetail.DoesNotExist:
            content = {
                "message": "Please contact admin"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def eoi_details(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role == AccountRole.EOI_USER:
        try:
            eoi = EOIDetail.objects.get(user_id=request.user.id)
            if request.method == 'GET':
                content = {
                    'eoi_detail_id': eoi.id,
                    'status': eoi.status,
                    'organisation_name': eoi.organisation_name,
                    'contact_person_name': eoi.contact_person_name,
                    'email': eoi.email,
                    'sectors': eoi.sectors,
                    'specialization': eoi.specialization,
                    'details_submitted_on': eoi.details_submitted_on,
                    'registration_document': eoi.registration_document.url if eoi.registration_document else None,
                    'declaration_document': eoi.declaration_document.url if eoi.declaration_document else None,
                    'detailed_proposal_document': eoi.detailed_proposal_document.url if eoi.detailed_proposal_document else None,
                    'created': eoi.created,
                    'updated': eoi.updated,
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            elif request.method == 'POST':
                organisation_name = request.POST.get('organisation_name', None)
                registration_document = request.FILES.get('registration_document', None)
                detailed_proposal_document = request.FILES.get('detailed_proposal_document', None)
                declaration_document = request.FILES.get('declaration_document', None)
                contact_person_name = request.POST.get('contact_person_name', None)
                mobile_number = request.POST.get('mobile_number', None)
                email = request.POST.get('email', None)
                sectors = request.POST.get('sectors', None)
                specialization = request.POST.get('specialization', None)
                if not organisation_name or not registration_document or not registration_document or \
                    not contact_person_name or not mobile_number or not email or \
                        not sectors or not specialization or not detailed_proposal_document or not declaration_document:

                    content = {
                        "message": "Please provide "
                                   "organisation_name/ "
                                   "registration_document/ "
                                   "contact_person_name/ "
                                   "mobile_number/ "
                                   "email/ "
                                   "sectors/ "
                                   "specialization/ "
                                   "detailed_proposal_document/ "
                                   "declaration_document"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                if eoi.status == 1:
                    content = {
                        "message": "Details already submitted",
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')

                eoi.organisation_name = organisation_name
                eoi.registration_document = registration_document
                eoi.contact_person_name = contact_person_name
                eoi.mobile_number = mobile_number
                eoi.email = email
                eoi.sectors = sectors
                eoi.specialization = specialization
                eoi.detailed_proposal_document = detailed_proposal_document
                eoi.declaration_document = declaration_document
                eoi.details_submitted_on = timezone.now()
                eoi.status = 1
                eoi.save()

                task = async_scp_with_eoi_files.delay(eoi.id)

                content = {
                    "message": "updated successfully",
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

        except EOIDetail.DoesNotExist:
            content = {
                "message": "Please contact admin"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def eoi_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.EOI_USER, AccountRole.NM_ADMIN_STAFF, AccountRole.SUPER_ADMIN, AccountRole.NM_ADMIN]:
        try:
            page = request.GET.get('page', 0)
            limit = request.GET.get('limit', 20)
            eoi_status = request.GET.get('status', None)
            sectors = request.GET.get('sectors', None)
            specialization = request.GET.get('specialization', None)
            search_text = request.GET.get('search_text', None)
            mode = request.GET.get('mode', None)
            download = request.GET.get('download', None)
            created_order_by = request.GET.get('created_order_by', '1')
            try:
                page = int(page)
                limit = int(limit)
            except:
                page = 0
                limit = 20
            query = {}
            if eoi_status:
                query['status'] = eoi_status
            else:
                eoi_status = 1
                query['status'] = 1
            if mode:
                query['mode'] = mode
            if sectors:
                query['sectors__icontains'] = sectors
            if specialization:
                query['specialization__icontains'] = specialization

            if search_text:
                query['organisation_name__icontains'] = search_text

            order_by_query = []
            if created_order_by == '0':
                order_by_query.append('created')
            else:
                order_by_query.append('-created')
            eois = EOIDetail.objects.filter(**query).order_by(*order_by_query)
            total_count = eois.count()
            if download == '1':
                # Get some data to write to the spreadsheet.
                headers = [
                    'eoi_detail_id',
                    'organisation_name',
                    'contact_person_name',
                    'mobile',
                    'email',
                    'status',
                    'sectors',
                    'specialization',
                    'details_submitted_on',
                    'mode',
                    'cost_per_student',
                    'created',
                ]
                data = [headers]
                for eoi in eois:
                    data.append([
                        eoi.id,
                        eoi.organisation_name,
                        eoi.contact_person_name,
                        eoi.mobile_number,
                        eoi.email,
                        eoi.status,
                        eoi.sectors,
                        eoi.specialization,
                        eoi.details_submitted_on.strftime('%d-%m-%Y %H:%M') if eoi.details_submitted_on else None,
                        eoi.mode,
                        eoi.cost_per_student,
                        eoi.created.strftime('%d-%m-%Y %H:%M') if eoi.created else None]
                    )
                response = HttpResponse(content_type='text/csv')
                response[
                    'Content-Disposition'] = 'attachment; filename="eoi_data.csv"'

                writer = csv.writer(response)
                writer.writerows(data)
                return response
            final_eois_list = []
            for eoi in eois[(page * limit): ((page*limit) + limit)]:
                temp_eoi = {
                    'eoi_detail_id': eoi.id,
                    'status': eoi.status,
                    'organisation_name': eoi.organisation_name,
                    'contact_person_name': eoi.contact_person_name,
                    'mobile': eoi.mobile_number,
                    'email': eoi.email,
                    'sectors': eoi.sectors,
                    'specialization': eoi.specialization,
                    'details_submitted_on': eoi.details_submitted_on,
                    'registration_document': eoi.registration_document.url if eoi.registration_document else None,
                    'declaration_document': eoi.declaration_document.url if eoi.declaration_document else None,
                    'detailed_proposal_document': eoi.detailed_proposal_document.url if eoi.detailed_proposal_document else None,
                    'mode': eoi.mode,
                    'cost_per_student': eoi.cost_per_student,
                    'created': eoi.created,
                    'updated': eoi.updated,
                }
                final_eois_list.append(temp_eoi)
            content = {
                "eois": final_eois_list,
                'filters': {
                    'page': page,
                    'limit': limit,
                    'total_count': total_count,
                    'sectors': sectors,
                    'status': eoi_status,
                    'specialization': specialization,
                    'search_text': search_text,
                    'mode': mode,
                    'download': download
                }
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except Exception as e:
            content = {
                "message": "Please try again",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def eoi_admin_details(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    eoi_id = request.GET.get('id', 0)
    if account_role in [AccountRole.EOI_USER, AccountRole.NM_ADMIN_STAFF, AccountRole.SUPER_ADMIN, AccountRole.NM_ADMIN]:
        try:
            eoi = EOIDetail.objects.get(id=eoi_id)
            content = {
                'eoi_detail_id': eoi.id,
                'status': eoi.status,
                'organisation_name': eoi.organisation_name,
                'contact_person_name': eoi.contact_person_name,
                'mobile': eoi.mobile_number,
                'email': eoi.email,
                'sectors': eoi.sectors,
                'specialization': eoi.specialization,
                'details_submitted_on': eoi.details_submitted_on,
                'registration_document': eoi.registration_document.url if eoi.registration_document else None,
                'declaration_document': eoi.declaration_document.url if eoi.declaration_document else None,
                'detailed_proposal_document': eoi.detailed_proposal_document.url if eoi.detailed_proposal_document else None,
                'mode': eoi.mode,
                'cost_per_student': eoi.cost_per_student,
                'created': eoi.created,
                'updated': eoi.updated,
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except EOIDetail.DoesNotExist:
            content = {
                "message": "EOI not found"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')