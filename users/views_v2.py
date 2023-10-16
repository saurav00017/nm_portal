import uuid

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
import yaml
from .models import User, UserDetail, PhoneNumberOtp
from datarepo.models import AccountRole
from datarepo.models import PaymentStatus, StudentRegistrationStatus
from college.models import CollegeSubscription, CollegeStatus
from student.models import Student, StudentPaymentDetail
from skillofferings.models import SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
from django.conf import settings
from django.utils.timezone import datetime, timedelta
import os
import razorpay
from nm_portal.config import Config
from college.models import College
from student.models import Student
import http
import json
from django.conf import settings
from django.template.loader import get_template
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives

from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP

from nm_portal.config import Config
from kp.models import KnowledgePartner

RAZORPAY_USERNAME = os.environ.get('RAZORPAY_KEY', '')
RAZORPAY_SECRET_KEY = os.environ.get('RAZORPAY_SECRET_KEY', '')

RAZORPAY_USERNAME = "rzp_test_TPNYwIheW2VPhC"
RAZORPAY_SECRET_KEY = "Y5mbKfcfdlwludb231FdHhiO"

nm_razorpay_client = razorpay.Client(auth=(RAZORPAY_USERNAME, RAZORPAY_SECRET_KEY))
nm_razorpay_client.set_app_details({"title": "django", "version": "3"})
from django.utils import timezone
import random
from psychometric.models import PsychometricResult
from psychometric.models import PsychometricPartner


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['account_role'] = user.account_role if user else None
        return token


@api_view(['POST'])
def request_otp_for_login_v2(request):
    phone_number = request.POST.get('phone_number', None)
    # roll_no = request.POST.get('roll_no', None)
    request_schema = '''
        phone_number:
            type: string
            empty: false
            required: true
            minlength: 10
       
        '''
    v = Validator()
    post_data = request.POST.dict()
    schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
    if v.validate(post_data, schema):
        required_roll_no = False
        try:
            student = Student.objects.get(phone_number=phone_number)
        except Student.MultipleObjectsReturned:
            required_roll_no = True
        except Student.DoesNotExist:
            student = Student.objects.create(
                phone_number=phone_number,
                is_free_user=True,
                college_id=2877  # Free College ID
            )

        try:
            _phone_number_obj = PhoneNumberOtp.objects.get(phone_number=phone_number)
        except PhoneNumberOtp.DoesNotExist:

            _phone_number_obj = PhoneNumberOtp.objects.create(phone_number=phone_number)
        # OTP Request Count Level check
        if _phone_number_obj.verification_expiry:
            if _phone_number_obj.verification_request_count >= 3:
                # verification_expiry already added 90 seconds from time of OTP generated
                if timezone.now() < _phone_number_obj.verification_expiry + timedelta(minutes=28, seconds=30):
                    content = {
                        'message': "OTP request limit exceed. Please try again after 30 minutes",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                else:
                    _phone_number_obj.verification_request_count = 0

        # OTP Attempt Count Level check
        if _phone_number_obj.verification_attempt and _phone_number_obj.verification_expiry:
            # verification_expiry already added 90 seconds from time of OTP generated
            if _phone_number_obj.verification_attempt >= 3 and timezone.now() < _phone_number_obj.verification_expiry + timedelta(minutes=28, seconds=30):
                content = {
                    'message': "OTP attempts limit exceed. Please try again after 30 minutes",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        verification_code = random.randint(10000, 99999)

        _phone_number_obj.verification_code = verification_code
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
                        "MSISDN": "91" + str(phone_number),
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
                _phone_number_obj.verification_expiry = timezone.now() + timedelta(seconds=90)
                _phone_number_obj.verification_attempt = None
                _phone_number_obj.verification_request_count += 1
                _phone_number_obj.save()
                content = {
                    'required_roll_no': required_roll_no,
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
            content = {
                'message': "Please try again later",
                "error": 'ConnectionRefusedError'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        # except Exception as e:
        #     content = {
        #         'message': "Please try again later",
        #         'error': str(e)
        #     }
        # return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "invalid request",
            'errors': v.errors
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def verify_login_with_otp_v2(request):
    phone_number = request.POST.get('phone_number', None)
    roll_no = request.POST.get('roll_no', None)
    verification_code = request.POST.get('otp', None)
    request_schema = '''
        phone_number:
            type: string
            empty: false
            required: true
            minlength: 10
        otp:
            type: string
            empty: false
            required: true
        roll_no:
            type: string
            empty: true
            required: false
        '''
    v = Validator()
    post_data = request.POST.dict()
    schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
    if v.validate(post_data, schema):
        try:
            _phone_number_obj = PhoneNumberOtp.objects.get(phone_number=phone_number)

            if _phone_number_obj.verification_attempt and _phone_number_obj.verification_expiry:
                # verification_expiry already added 90 seconds from time of OTP generated
                if _phone_number_obj.verification_attempt >= 3 and timezone.now() < _phone_number_obj.verification_expiry + timedelta(minutes=28, seconds=30):
                    content = {
                        'message': "OTP attempts limit exceed. Please try again after 30 minutes",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if not _phone_number_obj.verification_expiry:
                content = {
                    'message': "Please request the OTP",
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            if _phone_number_obj.verification_expiry >= timezone.now():
                if _phone_number_obj.verification_code != int(verification_code):
                    if _phone_number_obj.verification_attempt:
                        _phone_number_obj.verification_attempt += 1
                    else:
                        _phone_number_obj.verification_attempt = 1
                    _phone_number_obj.save()
                    if _phone_number_obj.verification_attempt >= 3:
                        error_message = "OTP attempts limit exceed. Please try again after 30 minutes"
                    else:
                        error_message = "Invalid OTP"
                    content = {
                        'message': error_message,
                        "attempt_count": _phone_number_obj.verification_attempt
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            _phone_number_obj.verification_code = None
            _phone_number_obj.verification_attempt = None
            _phone_number_obj.save()
            try:
                if roll_no:
                    student = Student.objects.get(phone_number=phone_number, roll_no__endswith=roll_no)
                else:
                    student = Student.objects.get(phone_number=phone_number)

            except Student.MultipleObjectsReturned:
                content = {
                    'message': "Please provide valid data",
                    'error': "Multi students"
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            except Student.DoesNotExist:
                content = {
                    'message': "Please provide valid data",
                    'error': "No students"
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            try:
                user_details = UserDetail.objects.get(student_id=student.id)
            except UserDetail.DoesNotExist:
                user = User.objects.create(
                    account_role=AccountRole.STUDENT,
                    username=phone_number
                )
                user_details = UserDetail.objects.create(student_id=student.id, user_id=user.id)

            refresh_token = MyTokenObtainPairSerializer.get_token(user=user_details.user)
            # print(user.account_role)
            content = {
                "mobile_number": student.phone_number,
                'refresh': str(refresh_token),
                'access': str(refresh_token.access_token)
            }
            return Response(content, status=status.HTTP_200_OK, content_type='application/json')
        except PhoneNumberOtp.DoesNotExist:
            content = {
                'message': "Please request OTP",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:
            content = {
                'message': "Please try again later",
                'error': str(e)
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "invalid request",
            'errors': v.errors
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

