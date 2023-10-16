from psychometric.models import PsychometricPartner
from psychometric.models import PsychometricResult
import random
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
import yaml
from .models import User, UserDetail
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

nm_razorpay_client = razorpay.Client(
    auth=(RAZORPAY_USERNAME, RAZORPAY_SECRET_KEY))
nm_razorpay_client.set_app_details({"title": "django", "version": "3"})


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['account_role'] = user.account_role if user else None
        return token


@api_view(['POST'])
def login(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    request_schema = '''
        username:
            type: string
            empty: false
            required: true
            minlength: 5
        password:
            type: string
            empty: false
            min: 6
            required: true
            minlength: 6
        '''
    v = Validator()
    post_data = request.POST.dict()
    schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
    if v.validate(post_data, schema):
        user = authenticate(username=username, password=password)
        if user:
            if user.account_role in [AccountRole.NM_ADMIN,
                                     AccountRole.NM_ADMIN_STAFF,
                                     AccountRole.DISTRICT_ADMIN,
                                     AccountRole.DISTRICT_ADMIN_STAFF,
                                     AccountRole.KNOWLEDGE_PARTNER,
                                     AccountRole.INDUSTRY_ADMIN,
                                     AccountRole.INDUSTRY_STAFF,
                                     AccountRole.INDUSTRY_USER,
                                     ]:
                refresh_token = MyTokenObtainPairSerializer.get_token(
                    user=user)
                # print(user.account_role)
                content = {
                    "username": user.username,
                    "name": user.name,
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token)
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            elif user.account_role == AccountRole.STUDENT:
                user_details = UserDetail.objects.select_related(
                    'student').get(user_id=user.id, student_id__isnull=False)

                if user_details.student_id:
                    get_student = user_details.student
                    if get_student.payment_status < 5:
                        get_student.payment_status = 5
                        get_student.save()

                refresh_token = MyTokenObtainPairSerializer.get_token(
                    user=user)
                # print(user.account_role)
                content = {
                    "username": user.username,
                    "name": user.name,
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token)
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            elif user.account_role in [AccountRole.COLLEGE_ADMIN,
                                       AccountRole.COLLEGE_ADMIN_STAFF,
                                       AccountRole.FACULTY

                                       ]:
                user_details = UserDetail.objects.select_related(
                    'college').get(user_id=user.id)

                if user_details.college_id:
                    if user_details.college.status == 1:
                        user_details.college.status = 2
                        user_details.college.save()

                refresh_token = MyTokenObtainPairSerializer.get_token(
                    user=user)
                # print(user.account_role)
                content = {
                    "username": user.username,
                    "name": user.name,
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token)
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

        content = {
            'message': "Please provide valid username/ password",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "invalid request",
            'errors': v.errors
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def profile_details(request):
    user = User.objects.get(id=request.user.id)
    content = {
        'username': user.username,
        "account_role": user.account_role,
        "name": user.name,
    }
    if user.account_role == AccountRole.KNOWLEDGE_PARTNER:
        kp = KnowledgePartner.objects.get(user=user)
        content['kp_details'] = {
            'name': kp.name,
            'description': kp.description,
            'website': kp.website,
            'logo': kp.logo.url if kp.logo else None,
            'is_fs': kp.is_fs,
        }
        return Response(content, status=status.HTTP_200_OK, content_type='application/json')

    user_details = UserDetail.objects.select_related('college', 'college__affiliated_university', 'college__district',
                                                     'student').filter(user_id=user.id).first()
    if user_details:
        if user_details.college_id:
            college = user_details.college
            if college.status == CollegeStatus.REGISTERED:
                try:
                    get_subscription = CollegeSubscription.objects.values('razorpay_order_id',
                                                                          'registration_fee').filter(
                        college_id=college.id, payment_status=PaymentStatus.INITIATE,
                        created__gte=datetime.now() - timedelta(minutes=5)
                    ).order_by('-id').first()
                    if get_subscription:
                        content['payment_details'] = {
                            "payment_status": PaymentStatus.INITIATE,
                            "order_id": get_subscription['razorpay_order_id'],
                            "amount": get_subscription['registration_fee'],
                        }
                    else:

                        try:
                            # Razor Pay
                            order_currency = 'INR'
                            order_receipt = 'NM_COLLEGE_' + str(timezone.now().strftime('%Y%m%d%H%M%S')) + "_" + str(
                                college.id)
                            razorpay_amount = Config.COLLEGE_SUBSCRIPTION_FEE
                            data = {
                                'amount': int(razorpay_amount),
                                'currency': order_currency,
                                'receipt': order_receipt,
                            }
                            # print(data)
                            order_details = nm_razorpay_client.order.create(
                                data=data)
                            razorpay_order_id = order_details['id']
                            new_subscription = CollegeSubscription.objects.create(
                                college_id=college.id,
                                registration_fee=razorpay_amount,
                                razorpay_order_id=razorpay_order_id,
                                razorpay_order_receipt=order_receipt,
                                razorpay_created_at=order_details[
                                    'created_at'] if 'created_at' in order_details else None,
                                payment_mode=0,  # Online
                                payment_status=PaymentStatus.INITIATE,  # initiate
                            )
                            content['payment_details'] = {
                                "payment_status": PaymentStatus.INITIATE,
                                "order_id": new_subscription.razorpay_order_id,
                                "amount": new_subscription.registration_fee / 100,
                            }
                        except Exception as e:
                            print("Error 1", e)
                except Exception as e:
                    print("Error 2", e)
            college_details = {
                'id': college.id,
                'status': college.status,
                'college_name': college.college_name,
                'release': college.mandatory_release,
                'college_code': college.college_code,
                'email': college.email,
                'is_mailed': college.is_mailed,
                'mobile': college.mobile,
                'college_type': college.college_type,
                'management_type': college.management_type,
                'year_of_establishment': college.year_of_establishment,
                'subscription_status': college.subscription_status,
                'external_assessment': college.external_assessment,

                'total_faculty_count': college.total_faculty_count,
                'total_1st_year_students_count': college.total_1st_year_students_count,
                'total_2nd_year_students_count': college.total_2nd_year_students_count,
                'total_3rd_year_students_count': college.total_3rd_year_students_count,
                'total_4th_year_students_count': college.total_4th_year_students_count,
                'registered_at': college.details_submitted_at,
                'address': college.address,
                'village': college.village,
                'town_city': college.town_city,
                'state': college.state,
                'pincode': college.pincode,
                'fax_number': college.fax_number,
                'website_url': str(college.website_url) if college.website_url else None,

                'expiry_date': college.expiry_date,
                'created': college.created,
                'principal_name': college.principal_name,
                'principal_mobile': college.principal_mobile,
                'principal_email': college.principal_email,
                'course_allocation': college.course_allocation,
                'affiliated_university': college.affiliated_university.name if college.affiliated_university_id else None,
                'district': college.district.name if college.district_id else None,

                'placement_name': college.placement_name,
                'placement_mobile': college.placement_mobile,
                'placement_email': college.placement_email,
            }
            content['college_details'] = dict(
                college_details) if college_details else None
        if user_details.student_id:
            student = user_details.student
            content['is_graduate'] = student.is_pass_out
            if student.registration_status == StudentRegistrationStatus.REGISTRATION_COMPLETE:
                try:
                    get_subscription = StudentPaymentDetail.objects.values('razorpay_order_id',
                                                                           'registration_fee').filter(
                        student_id=student.id, payment_status=PaymentStatus.INITIATE,
                        created__gte=datetime.now() - timedelta(minutes=5)
                    ).order_by('-id').first()
                    if get_subscription:
                        content['payment_details'] = {
                            "payment_status": PaymentStatus.INITIATE,
                            "order_id": get_subscription['razorpay_order_id'],
                            "amount": get_subscription['registration_fee'] / 100,
                        }
                    else:

                        try:
                            # Razor Pay
                            order_currency = 'INR'
                            order_receipt = 'NM_STUDENT_' + str(timezone.now().strftime('%Y%m%d%H%M%S')) + "_" + str(
                                student.id)
                            razorpay_amount = Config(caste=student.caste,
                                                     college_type=student.degree).STUDENT_SUBSCRIPTION_FEE
                            data = {
                                'amount': int(razorpay_amount),
                                'currency': order_currency,
                                'receipt': order_receipt,
                            }
                            # print(data)
                            order_details = nm_razorpay_client.order.create(
                                data=data)
                            razorpay_order_id = order_details['id']
                            new_subscription = StudentPaymentDetail.objects.create(
                                student_id=student.id,
                                registration_fee=razorpay_amount,
                                razorpay_order_id=razorpay_order_id,
                                razorpay_order_receipt=order_receipt,
                                razorpay_created_at=order_details[
                                    'created_at'] if 'created_at' in order_details else None,
                                payment_mode=0,  # Online
                                payment_status=PaymentStatus.INITIATE,  # initiate
                            )
                            content['payment_details'] = {
                                "payment_status": PaymentStatus.INITIATE,
                                "order_id": new_subscription.razorpay_order_id,
                                "amount": new_subscription.registration_fee / 100,
                            }
                        except Exception as e:
                            print("Student payment Details Error ", e)
                except Exception as e:
                    print("Student payment Details Error ", e)

            skill_offering_enrollments_ids = SKillOfferingEnrollment.objects.filter(
                student_id=student.id, is_mandatory=True).values_list('id', flat=True)
            is_feedback_submitted = SKillOfferingEnrollmentProgress.objects.filter(
                skill_offering_enrollment_id__in=skill_offering_enrollments_ids,
                feedback_status=True).exists()
            student_details = {
                'id': student.id,
                'college_name': student.college.college_name if student.college_id else None,
                'status': student.registration_status,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'roll_no': student.roll_no,
                'caste': student.caste,
                'phone_number': student.phone_number,
                'email': student.email,
                'aadhar_number': student.aadhar_number,
                'dob': student.dob,
                'sem': student.sem,
                'gender': student.gender,
                'degree': student.degree,
                'specialization': student.specialization,
                'affiliated_university_id': student.affiliated_university_id,
                'affiliated_university': student.affiliated_university.name if student.affiliated_university_id else None,
                # 'district': student.district.name if student.district_id else None,
                # 'current_address': student.current_address,
                # 'permanent_address': student.permanent_address,
                'hall_ticket_number': student.hall_ticket_number,
                'year_of_study': student.year_of_study,
                'year_of_graduation': student.year_of_graduation,
                'subscription_status': student.subscription_status,
                'expiry_date': student.expiry_date,
                'created': student.created,
                'current_address': {
                    'current_address': student.current_address,
                    # 'current_landmark': student.current_landmark,
                    'current_village': student.current_village,
                    'current_town_city': student.current_town_city,
                    'current_district': student.current_district,
                    'current_state': student.current_state,
                    'current_pincode': student.current_pincode,
                },
                'permanent_address': {
                    'permanent_address': student.permanent_address,
                    'permanent_village': student.permanent_village,
                    'permanent_town_city': student.permanent_town_city,
                    'permanent_district': student.permanent_district,
                    'permanent_state': student.permanent_state,
                    'permanent_pincode': student.permanent_pincode,
                }

            }
            college_details = {
                'college_name': student.college.college_name,
                'release': student.college.mandatory_release,
                'college_code': student.college.college_code,
                'college_email': student.college.email,
                'college_type': student.college.college_type,
                'management_type': student.college.management_type,

                'address': student.college.address,
                # 'landmark': get_college.landmark,
                # 'mandal': get_college.mandal,
                'village': student.college.village,
                'town_city': student.college.town_city,
                'state': student.college.state,
                'pincode': student.college.pincode,
                'fax_number': student.college.fax_number,
                'principal_name': student.college.principal_name,
                'principal_mobile': student.college.principal_mobile,
                'principal_email': student.college.principal_email,
                'website_url': str(student.college.website_url) if student.college.website_url else None,

                'affiliated_university': student.college.affiliated_university.name if student.college.affiliated_university_id else None,
                'district': student.college.district.name if student.college.district_id else None,

                'placement_name': student.college.placement_name,
                'placement_mobile': student.college.placement_mobile,
                'placement_email': student.college.placement_email,
            } if student.college_id else None
            content['is_feedback_not_submitted'] = not is_feedback_submitted if skill_offering_enrollments_ids else False
            content['student_details'] = dict(student_details)
            content['college_details'] = dict(
                college_details) if college_details else None
            # get pyschometric data
            try:
                psychometric_result_data = PsychometricResult.objects.filter(
                    student_id=student.id).first()
                if(psychometric_result_data):
                    temp = {
                        'id': psychometric_result_data.id,
                        'report_url': psychometric_result_data.report_url
                    }
                    content['psychometric_result'] = temp
                else:
                    content['psychometric_result'] = None
            except PsychometricResult.DoesNotExist:
                content['psychometric_result'] = None
    return Response(content, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.POST.get('current_password', None)
    new_password = request.POST.get('new_password', None)
    if current_password is None or new_password is None:
        context = {"message": "Please provide current_password/ new_password"}
        return Response(context, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    elif len(str(new_password).strip()) < 6:
        context = {
            "message": "Please provide new password with minium 6 characters"}
        return Response(context, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    user = User.objects.get(id=request.user.id)
    current_password_check = authenticate(
        username=user.username, password=current_password)
    if current_password_check:
        user.set_password(new_password)
        user.save()
        context = {"message": "Password updated successfully"}
        return Response(context, status=status.HTTP_200_OK, content_type='application/json')
    else:
        context = {"message": "Please provide valid current password"}
        return Response(context, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def forgot_username(request):
    email = request.POST.get('email', None)
    if email:
        user_id = None
        college_obj = College.objects.values(
            'id').filter(email__iexact=email).first()
        if college_obj:
            user_profile_obj = UserDetail.objects.values(
                'user_id').filter(college_id=college_obj['id']).first()
            user_id = user_profile_obj['user_id']
        else:
            student_obj = Student.objects.values(
                'id').filter(email__iexact=email).first()
            if student_obj:
                print("student_obj --> ", student_obj)
                user_profile_obj = UserDetail.objects.values(
                    'user_id').filter(student_id=student_obj['id']).first()
                print("user_profile_obj --> ", user_profile_obj)
                if user_profile_obj:
                    user_id = user_profile_obj['user_id']
        try:
            if user_id:
                user = User.objects.values('username').get(id=user_id)
            else:
                user = User.objects.values('username').filter(
                    email__iexact=email).first()
        except Exception as e:
            print("Error --> ", e)
            content = {
                'message': "Please provide valid email",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        if user:
            try:
                message = get_template("emails/forgot_username.html").render({
                    'username': user['username']
                })

                SMTPserver = 'mail.tn.gov.in'
                sender = 'naanmudhalvan@tn.gov.in'

                USERNAME = "naanmudhalvan"
                PASSWORD = "*nmportal2922*"
                # mail = EmailMultiAlternatives(
                #     "Forgot Username",
                #     message,
                #     from_email=from_email,
                #     to=[email, 'chandumanikumar4@gmail.com'],
                # )
                # mail.content_subtype = "html"
                # mail.mixed_subtype = 'related'
                # mail.attach_alternative(message, "text/html")
                # send = mail.send()
                subject = "Forgot Username"
                text_subtype = 'html'
                msg = MIMEText(message, text_subtype)
                msg['Subject'] = subject
                # some SMTP servers will do this automatically, not all
                msg['From'] = sender
                msg['Date'] = formatdate(localtime=True)

                conn = SMTP(host=SMTPserver, port=465)
                conn.set_debuglevel(False)
                conn.login(USERNAME, PASSWORD)
                conn.sendmail(sender, [email], msg.as_string())
                content = {
                    'message': "Email send your email address",
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            except Exception as e:
                print(e)
                content = {
                    'message': "Please try again later",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        else:
            content = {
                'message': "Please provide valid email",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "invalid request",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def forgot_password(request):
    email = request.POST.get('email', None)
    username = request.POST.get('username', None)
    if email or username:
        try:
            if username:
                user = User.objects.filter(username=username).exclude(
                    account_role=AccountRole.LMS_API_USER).first()
            else:
                user_id = None
                college_obj = College.objects.values(
                    'id').filter(email__iexact=email).first()
                if college_obj:
                    user_profile_obj = UserDetail.objects.values(
                        'user_id').filter(college_id=college_obj['id']).first()
                    user_id = user_profile_obj['user_id']
                else:
                    student_obj = Student.objects.values(
                        'id').filter(email__iexact=email).first()
                    if student_obj:
                        user_profile_obj = UserDetail.objects.values('user_id').filter(
                            student_id=student_obj['id']).first()
                        if user_profile_obj:
                            user_id = user_profile_obj['user_id']
                if user_id:
                    user = User.objects.filter(id=user_id).exclude(
                        account_role=AccountRole.LMS_API_USER).first()
                else:
                    user = User.objects.filter(email__iexact=email).exclude(
                        account_role=AccountRole.LMS_API_USER).first()
            try:
                user_profile = UserDetail.objects.get(user_id=user.id)
            except UserDetail.DoesNotExist:
                user_profile = UserDetail.objects.create(user_id=user.id)

            # OTP Request Count Level check
            if user_profile.verification_expiry:
                if user_profile.verification_request_count >= 3:
                    # verification_expiry already added 90 seconds from time of OTP generated
                    if timezone.now() < user_profile.verification_expiry + timedelta(minutes=28, seconds=30):
                        content = {
                            'message': "OTP request limit exceed. Please try again after 30 minutes",
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        user_profile.verification_request_count = 0

            # OTP Attempt Count Level check
            if user_profile.verification_attempt and user_profile.verification_expiry:
                # verification_expiry already added 90 seconds from time of OTP generated
                if user_profile.verification_attempt >= 3 and timezone.now() < user_profile.verification_expiry + timedelta(minutes=28, seconds=30):
                    content = {
                        'message': "OTP attempts limit exceed. Please try again after 30 minutes",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            verification_code = random.randint(10000, 99999)
            user_profile.verification_code = verification_code
            user_profile.verification_expiry = timezone.now() + timedelta(seconds=90)
            user_profile.verification_attempt = None
            user_profile.verification_request_count += 1
            user_profile.save()

            try:
                if user_profile.student_id:
                    email = user_profile.student.email
                elif user_profile.college_id:
                    email = user_profile.college.email
                else:
                    email = user_profile.user.email
                message = get_template("emails/verification_code.html").render({
                    'verification_code': verification_code
                })
                # from_email = settings.EMAIL_HOST_FROM
                # mail = EmailMultiAlternatives(
                #     "Reset password to Naan Mudhalvan Account",
                #     message,
                #     from_email=from_email,
                #     to=[user.email],
                # )
                # mail.content_subtype = "html"
                # mail.mixed_subtype = 'related'
                # mail.attach_alternative(message, "text/html")
                # send = mail.send()

                SMTPserver = 'mail.tn.gov.in'
                sender = 'naanmudhalvan@tn.gov.in'
                USERNAME = "naanmudhalvan"
                PASSWORD = "*nmportal2922*"
                # mail = EmailMultiAlternatives(
                #     "Forgot Username",
                #     message,
                #     from_email=from_email,
                #     to=[email, 'chandumanikumar4@gmail.com'],
                # )
                # mail.content_subtype = "html"
                # mail.mixed_subtype = 'related'
                # mail.attach_alternative(message, "text/html")
                # send = mail.send()
                subject = "Reset password to Naan Mudhalvan Account"
                text_subtype = 'html'
                msg = MIMEText(message, text_subtype)
                msg['Subject'] = subject
                # some SMTP servers will do this automatically, not all
                msg['From'] = sender
                msg['Date'] = formatdate(localtime=True)

                conn = SMTP(host=SMTPserver, port=465)
                conn.set_debuglevel(False)
                conn.login(USERNAME, PASSWORD)
                conn.sendmail(sender, [email], msg.as_string())

                content = {
                    'message': "Verification code send your email address",
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            except Exception as e:
                print(e)
                content = {
                    'message': "Please try again later",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except Exception as e:
            print(e)
            content = {
                'message': "Please provide valid email/ password",
                "error": str(e)
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "invalid request",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def forgot_password_reset(request):
    email = request.POST.get('email', None)
    username = request.POST.get('username', None)
    verification_code = request.POST.get('verification_code', None)
    new_password = request.POST.get('new_password', None)
    try:
        verification_code = int(verification_code)
    except:
        verification_code = 'invalid'
    if (email or username) and verification_code:

        try:
            if username:
                user = User.objects.filter(username=username).exclude(
                    account_role=AccountRole.LMS_API_USER).first()
            else:
                user_id = None
                college_obj = College.objects.values(
                    'id').filter(email__iexact=email).first()
                if college_obj:
                    user_profile_obj = UserDetail.objects.values(
                        'user_id').filter(college_id=college_obj['id']).first()
                    user_id = user_profile_obj['user_id']
                else:
                    student_obj = Student.objects.values(
                        'id').filter(email__iexact=email).first()
                    if student_obj:
                        user_profile_obj = UserDetail.objects.values('user_id').filter(
                            student_id=student_obj['id']).first()
                        if user_profile_obj:
                            user_id = user_profile_obj['user_id']
                if user_id:
                    user = User.objects.filter(id=user_id).exclude(
                        account_role=AccountRole.LMS_API_USER).first()
                else:
                    user = User.objects.filter(email__iexact=email).exclude(
                        account_role=AccountRole.LMS_API_USER).first()
            try:
                user_profile = UserDetail.objects.get(user_id=user.id)

                if user_profile.verification_attempt and user_profile.verification_expiry:
                    # verification_expiry already added 90 seconds from time of OTP generated
                    if user_profile.verification_attempt >= 3 and timezone.now() < user_profile.verification_expiry + timedelta(minutes=28, seconds=30):
                        content = {
                            'message': "OTP attempts limit exceed. Please try again after 30 minutes",
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                if user_profile.verification_expiry >= timezone.now():
                    if user_profile.verification_code != verification_code:
                        if user_profile.verification_attempt:
                            user_profile.verification_attempt += 1
                        else:
                            user_profile.verification_attempt = 1
                        user_profile.save()
                        if user_profile.verification_attempt >= 3:
                            error_message = "OTP attempts limit exceed. Please try again after 30 minutes"
                        else:
                            error_message = "Invalid OTP"
                        content = {
                            'message': error_message,
                            "attempt_count": user_profile.verification_attempt
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                    # print("new_password", new_password)
                    # print("user_profile", user_profile)
                    # print("user", user)
                    user.set_password(new_password)
                    user.save()
                    user_profile.verification_code = None
                    user_profile.verification_attempt = None
                    user_profile.save()

                    content = {
                        'message': "Password reset successfully",
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                else:
                    content = {
                        'message': "verification code has been expired",
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            except UserDetail.DoesNotExist:
                content = {
                    'message': "Please provide valid email/ username/ verification code",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except Exception as e:
            print(e)
            content = {
                'message': "Please provide valid email/ username/ verification code",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "Please provide valid email/ username/ verification code",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
