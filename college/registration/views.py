from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..models import RegistrationStepOne, College, CollegeSubscription, CollegeStatus
from datarepo.models import AccountRole, District, AffiliatedUniversity, PaymentStatus
from users.models import User, UserDetail
from users.views import MyTokenObtainPairSerializer
from cerberus import Validator
import yaml
import jwt
from django.conf import settings
from .tasks import async_task_college_invites
import json
from django.utils.timezone import timedelta, datetime
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import Context
from django.template.loader import get_template
from nm_portal.config import Config
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
import os

import razorpay

RAZORPAY_USERNAME = os.environ.get('RAZORPAY_KEY', '')
RAZORPAY_SECRET_KEY = os.environ.get('RAZORPAY_SECRET_KEY', '')

RAZORPAY_USERNAME = "rzp_test_TPNYwIheW2VPhC"
RAZORPAY_SECRET_KEY = "Y5mbKfcfdlwludb231FdHhiO"

nm_razorpay_client = razorpay.Client(auth=(RAZORPAY_USERNAME, RAZORPAY_SECRET_KEY))
nm_razorpay_client.set_app_details({"title": "django", "version": "3"})

# Create your views here.
"""
Endpoints
1. college_invites (POST)
2. college_registration_confirm (GET, POST)
3. college_registration_payment (Subscribe)
"""


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college_invites(request):
    """
    :param request: csv_file

    if -> account_role -> NM admin or NM staff
        1. create RegistrationStepOne Model
        2. start the celery task
            a. loop all the records and create TempRegistration record
    else  -> access Permission error

    :return:
    """
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    csv_file = request.FILES.get('csv_file', None)
    if csv_file:
        # NM admin or NM admin staff
        user_validation = User.objects.filter(id=request.user.id, account_role=account_role, is_active=1).exists()
        if user_validation and account_role in [AccountRole.NM_ADMIN]:
            new_step_one = RegistrationStepOne.objects.create(
                csv_file=csv_file,
                user_id=request.user.id
            )
            print(new_step_one)
            initiate_background_task = async_task_college_invites.delay(registration_step_one_id=new_step_one.id)

            print(initiate_background_task)
            content = {
                "message": "task initiated"
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        else:
            content = {
                "message": "You don't have the permissions"
            }
            return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    else:
        content = {
            "message": "Please provide file"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def resend_college_invites(request):
    """
    :param request: csv_file

    if -> account_role -> NM admin or NM staff
        1. get list of Colleges list
            [
                {
                    "invitation_id":"vfdvbfd",
                    "college_name":"college_name",
                    "email":"email",
                    "mobile":"mobile",
                }
            ]
        2. get college record from invitation ID
        3. resend the mails to colleges
    else  -> access Permission error

    :return:
    """
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        try:
            json_data = json.loads(request.body)
            if json_data:
                success_colleges_count = 0
                un_success_colleges_count = 0
                for record in json_data:
                    try:
                        get_college = College.objects.get(invitation_id=record['invitation_id'])
                        has_college_update = False
                        if 'college_name' in record:
                            get_college.college_name = record['college_name']
                            has_college_update = True
                        if 'email' in record:
                            get_college.email = record['email']
                            has_college_update = True
                        if 'mobile' in record:
                            get_college.mobile = record['mobile']
                            has_college_update = True
                        if has_college_update:
                            get_college.save()
                        try:
                            registration_url = settings.FRONT_END_URL + '/college-registration/' + str(
                                get_college.invitation_id)
                            message = get_template("emails/college_invite.html").render({
                                'registration_url': registration_url
                            })
                            print(get_college.email)
                            from_email = settings.EMAIL_HOST_FROM
                            mail = EmailMultiAlternatives(
                                "Invitation to Naan Mudhalvan",
                                message,
                                from_email=from_email,
                                to=[get_college.email],
                            )
                            mail.content_subtype = "html"
                            mail.mixed_subtype = 'related'
                            mail.attach_alternative(message, "text/html")
                            send = mail.send()
                            get_college.is_mailed = True
                            get_college.save()
                            success_colleges_count += 1
                        except Exception as e:
                            print(str(e))
                            un_success_colleges_count += 1
                    except College.DoesNotExist:
                        un_success_colleges_count += 1

                content = {
                    "message": "Mail send successfully",
                    'success_colleges_count': success_colleges_count,
                    'failed_colleges_count': un_success_colleges_count
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

            else:
                content = {
                    "message": "Please provide data"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except json.decoder.JSONDecodeError:
            content = {
                "message": "Please provide valid data"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST'])
def college_registration(request, invitation_id: str):
    """
    :Public_endpoint
    :param request: invitation_id

    if invitation_id is valid from College Model with status=0
        if :GET - get_details
            :return College basic details
        elif :POST - update_details
            1. update the details
            2. generate razor pay ID
            :return razor details

    else
        :return Invalid invitation_id
    """

    if invitation_id:
        if request.method == 'GET':
            try:
                get_college = College.objects.values(
                    'id',
                    'college_name',
                    'email',
                    'mobile',
                    'status',
                ).get(invitation_id=invitation_id, status__in=[0, 1], subscription_status=False)
                college_id = get_college['id']
                college_status = get_college['status']
                del get_college['id']
                del get_college['status']
                content = {
                    'payment_details': None,
                    'college_details': dict(get_college)
                }
                if college_status == CollegeStatus.REGISTERED:
                    get_subscription = CollegeSubscription.objects.values('razorpay_order_id',
                                                                          'registration_fee').filter(
                        college_id=college_id, payment_status=PaymentStatus.INITIATE).order_by('-id').first()
                    if get_subscription:
                        content['payment_details'] = {
                            "payment_status": PaymentStatus.INITIATE,
                            "order_id": get_subscription['razorpay_order_id'],
                            "amount": get_subscription['registration_fee'] / 100,
                        }

                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:

                content = {
                    "message": "invalid invitation ID"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        elif request.method == 'POST':
            college_name = request.POST.get('college_name', None)
            college_code = request.POST.get('college_code', None)
            college_type = request.POST.get('college_type', None)
            mobile = request.POST.get('mobile', None)
            email = request.POST.get('email', None)
            affiliated_university_id = request.POST.get('affiliated_university_id', None)
            management_type = request.POST.get('management_type', None)
            year_of_establishment = request.POST.get('year_of_establishment', None)
            total_faculty_count = request.POST.get('total_faculty_count', None)
            total_1st_year_students_count = request.POST.get('total_1st_year_students_count', None)
            total_2nd_year_students_count = request.POST.get('total_2nd_year_students_count', None)
            total_3rd_year_students_count = request.POST.get('total_3rd_year_students_count', None)
            total_4th_year_students_count = request.POST.get('total_4th_year_students_count', None)
            try:
                total_4th_year_students_count = int(total_4th_year_students_count)
            except:
                total_4th_year_students_count = 0
            address = request.POST.get('address', None)
            # landmark = request.POST.get('landmark', None)
            # mandal = request.POST.get('mandal', None)
            town_city = request.POST.get('town_city', None)
            village = request.POST.get('village', None)
            district_id = request.POST.get('district_id', None)
            state = request.POST.get('state', None)
            pincode = request.POST.get('pincode', None)
            fax_number = request.POST.get('fax_number', None)
            website_url = request.POST.get('website_url', None)

            # user_credentials
            account_credentials = request.POST.get('account_credentials', None)
            """
            :account_credentials example
            {
                "admin_username": "college_admin",
                "admin_password": "admin_pass",
                "staff_list": [
                    {"username":"staff1", "email":"staff@gmail.com", "password":"staff_pass"}
                ]
            }
            """
            request_schema = '''
                college_name:
                    type: string
                    empty: false
                    required: true
                college_code:
                    type: string
                    empty: false
                    required: true
                college_type:
                    type: string
                    empty: false
                    required: true
                mobile:
                    type: string
                    empty: false
                    required: true
                email:
                    type: string
                    empty: false
                    required: true
                affiliated_university_id:
                    type: string
                    empty: false
                    required: true
                management_type:
                    type: string
                    empty: false
                    required: true
                year_of_establishment:
                    type: string
                    empty: false
                    required: true
                    min: 4
                    minlength: 4
                    maxlength: 4
                total_faculty_count:
                    type: string
                    empty: false
                    required: true
                total_1st_year_students_count:
                    type: string
                    empty: false
                    required: true
                total_2nd_year_students_count:
                    type: string
                    empty: false
                    required: true
                total_3rd_year_students_count:
                    type: string
                    empty: false
                    required: true
                total_4th_year_students_count:
                    type: string
                    empty: false
                    required: true
                address:
                    type: string
                    empty: false
                    required: true
                town_city:
                    type: string
                    empty: true
                    required: false
                village:
                    type: string
                    empty: true
                    required: false
                district_id:
                    type: string
                    empty: true
                    required: false
                state:
                    type: string
                    empty: true
                    required: false
                pincode:
                    type: string
                    empty: true
                    required: false
                    min: 6
                    minlength: 6
                    maxlength: 6
                    
                fax_number:
                    type: string
                    empty: true
                    required: false
                website_url:
                    type: string
                    empty: true
                    required: false
                account_credentials:
                    type: string
                    empty: false
                    required: true
                '''
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    account_credentials = json.loads(account_credentials)
                    admin_username = account_credentials['admin_username'] if 'admin_username' in account_credentials else None
                    admin_password = account_credentials[
                        'admin_password'] if 'admin_password' in account_credentials else None
                    staff_credentials_list = account_credentials[
                        'staff_list'] if 'staff_list' in account_credentials else None

                    if admin_username and len(str(admin_password)) >= 8:
                        try:
                            get_college = College.objects.get(invitation_id=invitation_id, status=0)
                            try:
                                get_affiliated_university = AffiliatedUniversity.objects.get(
                                    id=int(affiliated_university_id))
                            except AffiliatedUniversity.DoesNotExist:
                                content = {
                                    "message": "Please provide valid affiliated university ID"
                                }
                                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                            try:
                                get_district = District.objects.get(id=int(district_id))
                            except District.DoesNotExist:
                                content = {
                                    "message": "Please provide valid district ID"
                                }
                                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                            try:
                                get_college.college_name = college_name
                                get_college.college_type = int(college_type)
                                get_college.college_code = college_code
                                get_college.mobile = mobile
                                get_college.email = email
                                get_college.affiliated_university_id = int(affiliated_university_id)
                                get_college.management_type = int(management_type)
                                get_college.year_of_establishment = int(year_of_establishment)
                                get_college.total_faculty_count = int(total_faculty_count)
                                get_college.total_1st_year_students_count = int(total_1st_year_students_count)
                                get_college.total_2nd_year_students_count = int(total_2nd_year_students_count)
                                get_college.total_3rd_year_students_count = int(total_3rd_year_students_count)
                                get_college.total_4th_year_students_count = int(total_4th_year_students_count)
                                get_college.address = address
                                get_college.town_city = town_city
                                get_college.village = village
                                get_college.district_id = int(district_id)
                                get_college.pincode = int(pincode)
                                get_college.state = state
                                get_college.fax_number = fax_number
                                get_college.website_url = website_url
                                # create college_admin
                                new_admin_user = User.create_registered_user(
                                    username=admin_username,
                                    password=admin_password,
                                    mobile=mobile,
                                    email=email,
                                    account_role=AccountRole.COLLEGE_ADMIN,
                                    college_id=get_college.id,
                                )
                                if staff_credentials_list:
                                    for staff in staff_credentials_list:
                                        '''{
                                        "username":"staff1", 
                                        "email":"staff@gmail.com",
                                        "password":"staff_pass"
                                        }'''
                                        staff_username = staff['username'] if 'username' in staff else None
                                        staff_email = staff['email'] if 'email' in staff else None
                                        staff_password = staff['password'] if 'password' in staff else None
                                        if staff_username and staff_password:
                                            new_staff_user = User.create_registered_user(
                                                username=staff_username,
                                                password=staff_password,
                                                mobile=mobile,
                                                email=staff_email if staff_email else email,
                                                account_role=AccountRole.COLLEGE_ADMIN_STAFF,
                                                college_id=get_college.id,
                                            )
                                get_college.status = 1
                                get_college.save()
                                try:
                                    # Razor Pay
                                    order_currency = 'INR'
                                    order_receipt = 'NM_C' + invitation_id
                                    razorpay_amount = Config.COLLEGE_SUBSCRIPTION_FEE
                                    data = {
                                        'amount': int(razorpay_amount),
                                        'currency': order_currency,
                                        'receipt': order_receipt,
                                    }
                                    # print(data)
                                    order_details = nm_razorpay_client.order.create(data=data)
                                    print(order_details)
                                    razorpay_order_id = order_details['id']
                                    new_college_subscription = CollegeSubscription.objects.create(
                                        college_id=get_college.id,
                                        registration_fee=razorpay_amount / 100,
                                        razorpay_order_id=razorpay_order_id,
                                        razorpay_order_receipt=order_receipt,
                                        razorpay_created_at=order_details[
                                            'created_at'] if 'created_at' in order_details else None,
                                        payment_mode=0,  # Online
                                        payment_status=PaymentStatus.INITIATE,  # initiate
                                    )

                                    admin_refresh_token = MyTokenObtainPairSerializer.get_token(new_admin_user)
                                    content = {
                                        "college_name": get_college.college_name,
                                        'payment_status': 0,  # Need to pay
                                        'order_id': razorpay_order_id,
                                        'amount': razorpay_amount / 100,
                                        "username": new_admin_user.username,
                                        "name": new_admin_user.name,
                                        'refresh': str(admin_refresh_token),
                                        'access': str(admin_refresh_token.access_token)
                                    }
                                    return Response(content, status.HTTP_200_OK, content_type='application/json')

                                except Exception as e:
                                    content = {
                                        "message": "Registration done successfully. Payment",
                                        'error': str(e)
                                    }
                                    return Response(content, status.HTTP_400_BAD_REQUEST,
                                                    content_type='application/json')

                            except Exception as e:
                                content = {
                                    "message": "Please provide valid data",
                                    'error': str(e)
                                }
                                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                        except College.DoesNotExist:

                            content = {
                                "message": "invalid invitation ID/ already registered"
                            }
                            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        content = {
                            "message": "Please provide valid college admin credentials"
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Exception as e:
                    content = {
                        "message": "Please provide valid credentials",
                        'error': str(e)
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "Please provide invitation ID"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def confirm_registration_payment(request):
    original_order_id = request.POST.get('order_id', None)
    razorpay_payment_id = request.POST.get('razorpay_payment_id', None)
    razorpay_order_id = request.POST.get('razorpay_order_id', None)
    razorpay_signature = request.POST.get('razorpay_signature', None)
    if original_order_id is None or razorpay_payment_id is None or razorpay_order_id is None or razorpay_signature is None:
        content = {
            'response_type': 0,
            'message': 'order id/ razorpay payment id/ razorpay order id/ razorpay signature is required'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            get_subscription = CollegeSubscription.objects.select_related('college').get(
                razorpay_order_id=original_order_id, payment_status=PaymentStatus.INITIATE)

            get_subscription.razorpay_order_id = razorpay_order_id
            get_subscription.razorpay_payment_id = razorpay_payment_id
            get_subscription.razorpay_signature = razorpay_signature
            get_subscription.save()
            params_dict = {
                'original_order_id': get_subscription.razorpay_order_id,
                'razorpay_order_id': get_subscription.razorpay_order_id,
                'razorpay_payment_id': get_subscription.razorpay_payment_id,
                'razorpay_signature': get_subscription.razorpay_signature,
            }
            nm_razorpay_client.utility.verify_payment_signature(params_dict)

            get_subscription.payment_done_at = datetime.now()
            get_subscription.status = PaymentStatus.SUCCESS
            get_subscription.save()
            get_subscription.college.status = CollegeStatus.PAYMENT_DONE
            get_subscription.college.subscription_status = True
            get_subscription.college.expiry_date = (
                        datetime.now() + timedelta(days=365 * Config.COLLEGE_SUBSCRIPTION_YEARS)).date()
            get_subscription.college.save()
            get_subscription.save()

            content = {
                'message': "payment done successful"
            }
            return Response(content, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:

            get_subscription.status = PaymentStatus.FAILED
            get_subscription.save()
            content = {
                'message': "Invalid info"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        except CollegeSubscription.DoesNotExist:
            content = {
                'message': "Invalid order id"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def mail_test(request):
    """
    Send email to customer with order details.
    """
    try:
        registration_url = 'http://0.0.0.0:2022/registration/%s' % "werfefsf"
        message = get_template("emails/college_invite.html").render({
            'registration_url': registration_url
        })
        FROM_EAMIL = settings.EMAIL_HOST_FROM
        mail = EmailMessage(
            subject="Order confirmation",
            body=message,
            from_email=FROM_EAMIL,
            to=['chandumanikumar5@gmail.com'],
            reply_to=[FROM_EAMIL],
        )
        mail.content_subtype = "html"
        send = mail.send()

        content = {
            'mail': str(send),
            'mail_dir': dir(send),
            'date': (datetime.now() + timedelta(days=365)).date()
        }
        return Response(content, status=status.HTTP_200_OK)
    except Exception as e:
        content = {
            'error': str(e),
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
