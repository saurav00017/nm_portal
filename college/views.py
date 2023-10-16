from django.db.models import Count
from datarepo.models import CollegeType, CollegeManagementType
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
from datarepo.models import AccountRole
from .models import College, CollegeStatus, CollegeSubscription, CollegeOtpVerification, CollegeFaculty, \
    FacultyFDPDetails
import yaml
import jwt
from django.conf import settings
from django.db.models.functions import Lower
from django.db.models import Q
from users.models import User, UserDetail
from student.models import Student
from lms.models import StudentCourse
from django.db import IntegrityError
import random
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP
import http.client
import json
from django.utils.timezone import datetime, timedelta

# Create your views here.
"""
1. colleges (GET)
2. college (GET, UPDATE)
"""


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def colleges(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    order_by_filter = []
    try:
        affiliated_university_id = request.GET.get(
            'affiliated_university_id', None)
        if affiliated_university_id:
            query['affiliated_university_id'] = int(affiliated_university_id)

        district_id = request.GET.get('district_id', None)
        if district_id:
            query['district_id'] = int(district_id)

        management_type = request.GET.get('management_type', None)
        if management_type:
            query['management_type'] = int(management_type)

        college_type = request.GET.get('college_type', None)
        if college_type:
            query['college_type'] = int(college_type)

        subscription = request.GET.get('subscription', None)
        if subscription:
            query['subscription_status'] = int(subscription)

        college_status = request.GET.get('status', None)
        if college_status:
            query['status'] = int(college_status)

        or_query_list = []
        search_txt = request.GET.get('search_txt', None)
        if search_txt:
            or_query_list.append(
                Q(
                    Q(college_name__istartswith=search_txt) |
                    Q(college_code__istartswith=search_txt) |
                    Q(email__istartswith=search_txt) |
                    Q(mobile__istartswith=search_txt)
                )
            )

        odb_college_name = request.GET.get('odb_college_name', None)
        if odb_college_name:
            order_by_filter.append(
                '-name' if odb_college_name == '1' else 'name')

    except Exception as e:
        content = {"message": "Please provide valid filters"}
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        colleges_count = College.objects.filter(
            *or_query_list, **query).count()
        colleges_verified_count = College.objects.filter(*or_query_list, **query).filter(
            is_students_verified=True).count()
        colleges_list = College.objects.annotate(name=Lower('college_name')).select_related('affiliated_university',
                                                                                            'district').values(
            'id',
            'invitation_id',
            'status',
            'college_name',
            'college_code',
            'spoc_name',
            'email',
            'is_mailed',
            'mobile',
            'college_type',
            'management_type',
            'year_of_establishment',
            'subscription_status',
            'expiry_date',
            'created',
            'is_students_verified',
            'affiliated_university__name',
            'district__name',
            'district_id',
            'zone_id',
            'pincode',
        ).filter(*or_query_list, **query).order_by(*order_by_filter, '-created')[
            (page * limit): ((page * limit) + limit)]

        final_college_list = []
        for college_record in colleges_list:
            college_record['affiliated_university'] = college_record['affiliated_university__name']
            del college_record['affiliated_university__name']
            college_record['district'] = college_record['district__name']
            del college_record['district__name']
            final_college_list.append(college_record)

        content = {
            'colleges_list': final_college_list,
            'total_count': colleges_count,
            'colleges_verified_count': colleges_verified_count,
            'page': page,
            'limit': limit,
            'filters': {
                'district_id': district_id,
                'affiliated_university_id': affiliated_university_id,
                'management_type': management_type,
                'college_type': college_type,
                'subscription': subscription,
                'search_txt': search_txt,
            },
            'order_by': {
                'odb_college_name': odb_college_name
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_colleges_dropdown(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        colleges_list = College.objects.annotate(name=Lower('college_name')).values(
            'id',
            'name',
        ).filter(status__gte=CollegeStatus.REGISTERED).order_by('name')

        content = {
            'colleges_list': colleges_list
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST', 'PATCH'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college_counter(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        # all_students =
        content = {
            "total_students_first_login": Student.objects.filter(payment_status=5, is_pass_out=False).count(),
            "total_students_verified_by_colleges": Student.objects.filter(verification_status=1,
                                                                          is_pass_out=False).count(),
            "total_colleges_completed_verification_students": College.objects.filter(is_students_verified=1,
                                                                                     is_pass_out=False).count(),
            "total_colleges_students_verified": College.objects.filter(is_students_verified=1,
                                                                       is_pass_out=False).count(),
            "total_online_courses_subsections": StudentCourse.objects.count(),
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST', 'PATCH'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college(request, college_id: int = 0):
    """
    if -> account_role is NM_ADMIN or NM_ADMIN_STAFF
        :param college_id
        :param request
        :return college details
    elif -> account_role COLLEGE_ADMIN or COLLEGE_ADMIN_STAFF
        :return college details

    :return:
    """
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        if request.method == 'GET':
            try:
                get_college = College.objects.get(id=college_id)
                college_details = {
                    'college_name': get_college.college_name,
                    'invitation_id': get_college.invitation_id,
                    'id': get_college.id,
                    'college_code': get_college.college_code,
                    'email': get_college.email,
                    'is_mailed': get_college.is_mailed,
                    'mobile': get_college.mobile,
                    'zone_id': get_college.zone_id,
                    'spoc_name': get_college.spoc_name,
                    'college_type': get_college.college_type,
                    'affiliated_university_id': get_college.affiliated_university_id,
                    'affiliated_university': get_college.affiliated_university.name if get_college.affiliated_university_id else None,
                    'district_id': get_college.district_id,
                    'district': get_college.district.name if get_college.district_id else None,
                    'management_type': get_college.management_type,
                    'year_of_establishment': get_college.year_of_establishment,
                    'total_faculty_count': get_college.total_faculty_count,
                    'total_1st_year_students_count': get_college.total_1st_year_students_count,
                    'total_2nd_year_students_count': get_college.total_2nd_year_students_count,
                    'total_3rd_year_students_count': get_college.total_3rd_year_students_count,
                    'total_4th_year_students_count': get_college.total_4th_year_students_count,
                    'total_students_count': get_college.total_students_count,
                    'details_submitted_at': get_college.details_submitted_at,
                    'address': get_college.address,
                    # 'landmark': get_college.landmark,
                    # 'mandal': get_college.mandal,
                    'village': get_college.village,
                    'town_city': get_college.town_city,
                    'state': get_college.state,
                    'pincode': get_college.pincode,
                    'fax_number': get_college.fax_number,
                    'website_url': get_college.website_url,
                    'subscription_status': get_college.subscription_status,
                    'expiry_date': get_college.expiry_date,
                    'created': get_college.created,
                    'updated': get_college.updated,
                    'principal_name': get_college.principal_name,
                    'principal_mobile': get_college.principal_mobile,
                    'principal_email': get_college.principal_email,
                    'placement_name': get_college.placement_name,
                    'placement_mobile': get_college.placement_mobile,
                    'placement_email': get_college.placement_email,
                }

                users_list = UserDetail.objects.select_related('user').filter(
                    college_id=get_college.id).order_by('user__account_role', Lower('user__name'))
                final_users_list = [
                    {
                        'user_id': spoc.user_id,
                        'name': spoc.user.name,
                        'email': spoc.user.email,
                        'mobile': spoc.user.mobile,
                        'account_role': spoc.user.account_role,
                    } for spoc in users_list
                ]
                content = {
                    "college_details": college_details,
                    'users_list': final_users_list
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:

                content = {
                    "message": "College does not exist"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        elif request.method == 'PATCH':
            try:
                get_college = College.objects.get(id=college_id)
                is_send_invite = request.data.get('is_send_invite', None)
                is_send_invite = True if is_send_invite == 'true' else False
                if is_send_invite:
                    username = ''
                    #
                    if get_college.college_type == 2:
                        # Engineering
                        username = 'tnengg' + str(get_college.college_code)
                    elif get_college.college_type == 1:
                        # Arts & Science
                        username = 'tnas' + str(get_college.college_code)
                    elif get_college.college_type == 4:
                        username = 'tnpoly0' + str(get_college.college_code)
                    username = username.lower()
                    password = str(random.randint(100000, 999999))
                    error_message = None
                    try:
                        user_info = User.objects.get(username=username)
                        user_info.set_password(password)
                        user_info.save()
                    except User.DoesNotExist:
                        new_user = User.create_registered_user(
                            username=username,
                            college_id=get_college.id,
                            password=password,
                            account_role=6,
                            email='',
                            mobile='',
                        )
                        new_user.save()
                    """
                    """
                    SMTPserver = settings.CUSTOM_SMTP_HOST
                    sender = settings.CUSTOM_SMTP_SENDER

                    USERNAME = settings.CUSTOM_SMTP_USERNAME
                    PASSWORD = settings.CUSTOM_SMTP_PASSWORD

                    content = f"""\
                    Dear Team,

                    Greetings from  Naan Mudhalvan team. Thank you for your interest in Naan Mudhalvan programme

                    Please find your URL and login credentials for Naan Mudhalvan platform

                    URL to login : https://portal.naanmudhalvan.tn.gov.in/login
                                Username : {username}
                                Password : {password}

                    Please feel free to contact us on support email - support@naanmudhalvan.in

                    Thanks,
                    Naan Mudhalvan Team,
                    Tamil Nadu Skill Development Corporation


                    This is an automatically generated email from the Naan Mudhalvan Platform. Please do not reply to the sender of this email.


                    """

                    subject = "Invitation to Naan Mudhalvan"
                    text_subtype = 'plain'
                    msg = MIMEText(content, text_subtype)
                    msg['Subject'] = subject
                    # some SMTP servers will do this automatically, not all
                    msg['From'] = sender
                    msg['Date'] = formatdate(localtime=True)

                    conn = SMTP(host=SMTPserver, port=465)
                    conn.set_debuglevel(False)
                    conn.login(USERNAME, PASSWORD)
                    is_email_sent = None
                    try:
                        conn.sendmail(
                            sender, [get_college.email], msg.as_string())
                        is_email_sent = True
                    except Exception as e:
                        print("\n\n\nSEND MAIL\n\n\n", str(e), "\n\n\n")
                        is_email_sent = False
                    finally:
                        conn.quit()
                    is_sms_sent = None
                    if get_college.mobile is not None:
                        try:
                            conn = http.client.HTTPConnection(
                                "digimate.airtel.in:15181")
                            payload = json.dumps({
                                "keyword": "DEMO",
                                "timeStamp": "1659688504",
                                "dataSet": [
                                    {
                                        "UNIQUE_ID": "16596885049652",
                                        "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                        "OA": "NMGOVT",
                                        "MSISDN": "91" + str(get_college.mobile),
                                        "CHANNEL": "SMS",
                                        "CAMPAIGN_NAME": "tnega_u",
                                        "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                        "USER_NAME": "tnega_tnsd",
                                        "DLT_TM_ID": "1001096933494158",
                                        "DLT_CT_ID": "1007269191406004910",
                                        "DLT_PE_ID": "1001857722001387178"
                                    }
                                ]
                            })
                            headers = {
                                'Content-Type': 'application/json'
                            }

                            conn.request(
                                "GET", "/BULK_API/InstantJsonPush", payload, headers)
                            res = conn.getresponse()
                            data = res.read()
                            sms_response = data.decode("utf-8")
                            if sms_response == 'true':
                                is_sms_sent = True
                            else:
                                is_sms_sent = False
                        except Exception as e:
                            print("\n\n\nSEND SMS\n\n\n", str(e), "\n\n\n")
                            is_sms_sent = False
                    get_college.status = 1
                    get_college.save()
                    content = {
                        "message": "Invitation sent successfully",
                        "data": {
                            "is_email_sent": is_email_sent,
                            "is_sms_sent": is_sms_sent,
                            'username': username,
                            'password': password
                        }
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                college_name = request.POST.get('college_name', None)
                college_code = request.POST.get('college_code', None)
                spoc_name = request.POST.get('spoc_name', None)
                email = request.POST.get('email', None)
                mobile = request.POST.get('mobile', None)
                zone_id = request.POST.get('zone_id', None)
                district_id = request.POST.get('district_id', None)
                pincode = request.POST.get('pincode', None)
                get_college.college_name = college_name if college_name is not None else get_college.college_name
                get_college.college_code = college_code if college_code is not None else get_college.college_code
                get_college.spoc_name = spoc_name if spoc_name is not None else get_college.spoc_name
                get_college.email = email if email is not None else get_college.email
                get_college.mobile = mobile if mobile is not None else get_college.mobile
                get_college.zone_id = zone_id if zone_id is not None else get_college.zone_id
                get_college.district_id = district_id if district_id is not None else get_college.district_id
                get_college.pincode = pincode if pincode is not None else get_college.pincode
                get_college.save()
                content = {
                    "message": "College details updated successfully"
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:
                content = {
                    "message": "College does not exist"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        elif request.method == 'POST':
            college_name = request.POST.get('college_name', None)
            college_code = request.POST.get('college_code', None)
            spoc_name = request.POST.get('spoc_name', None)
            email = request.POST.get('email', None)
            mobile = request.POST.get('mobile', None)
            zone_id = request.POST.get('zone_id', None)
            district_id = request.POST.get('district_id', None)
            pincode = request.POST.get('pincode', None)
            address = request.POST.get('address', None)
            college_type = request.POST.get('college_type', None)

            """
            placement_ name, email, mobile
            """

            if college_type is not None and college_type in ['1', '2', '3', '4', '5', '6']:
                college_type = int(college_type)
            elif college_type is not None and college_type not in ['1', '2', '3', '4', '5', '6']:
                content = {
                    "message": "College type is not valid"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if college_name is None or college_code is None or spoc_name is None or email is None or mobile is None or zone_id is None or district_id is None or pincode is None or address is None or college_type is None:
                content = {
                    "message": "All fields are required"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if College.objects.filter(college_code=college_code).exists():
                content = {
                    "message": "College code already exists"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            try:
                new_college = College.objects.create(
                    college_name=college_name,
                    college_code=college_code,
                    spoc_name=spoc_name,
                    email=email,
                    mobile=mobile,
                    zone_id=zone_id,
                    district_id=district_id,
                    pincode=pincode,
                    address=address,
                    college_type=college_type,
                    status=0
                )
                new_college.save()
                content = {
                    "message": "College created successfully"
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except IntegrityError as e:
                content = {
                    "message": "College code already exists",
                    "tech_str": str(e)
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    elif account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        user_details = UserDetail.objects.select_related(
            'college').get(user_id=decoded_data['user_id'])
        get_college = user_details.college
        is_students_verified = request.POST.get('is_students_verified', False)
        is_students_verified = True if is_students_verified == 'true' else False
        if is_students_verified:
            get_college.is_students_verified = True
            get_college.save()
            content = {
                "message": "Students verified"
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        principal_name = request.POST.get('principal_name', None)
        principal_mobile = request.POST.get('principal_mobile', None)
        principal_email = request.POST.get('principal_email', None)
        get_college.principal_name = principal_name if principal_name is not None else get_college.principal_name
        get_college.principal_mobile = principal_mobile if principal_mobile is not None else get_college.principal_mobile
        get_college.principal_email = principal_email if principal_email is not None else get_college.principal_email

        placement_name = request.POST.get('placement_name', None)
        placement_mobile = request.POST.get('placement_mobile', None)
        placement_email = request.POST.get('placement_email', None)
        get_college.placement_name = placement_name if placement_name is not None else get_college.placement_name
        get_college.placement_mobile = placement_mobile if placement_mobile is not None else get_college.placement_mobile
        get_college.placement_email = placement_email if placement_email is not None else get_college.placement_email

        get_college.save()
        content = {
            "message": "College details updated successfully"
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college_external_assessment(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        if request.method == 'GET':
            college_id = request.GET.get('college_id', None)
            if not college_id:
                content = {
                    "message": "Please provide college_id"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            try:
                get_college = College.objects.get(id=college_id)

                content = {
                    "college_id": get_college.id,
                    "external_assessment": get_college.external_assessment,
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:

                content = {
                    "message": "College does not exist"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        elif request.method == 'POST':
            college_id = request.POST.get('college_id', None)
            external_assessment = request.POST.get('external_assessment', None)
            try:
                external_assessment = int(external_assessment)
            except:
                external_assessment = None
            if college_id is None or external_assessment is None:
                content = {
                    "message": "Please provide college_id/ external_assessment"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            try:
                get_college = College.objects.get(id=college_id)
                get_college.external_assessment = external_assessment
                get_college.save()
                content = {
                    "message": "Updated successfully",
                    "college_id": get_college.id,
                    "external_assessment": get_college.external_assessment,
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:

                content = {
                    "message": "College does not exist"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    elif account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        if request.method == 'GET':
            user_details = UserDetail.objects.get(user_id=request.user.id)

            try:
                get_college = College.objects.get(id=user_details.college_id)

                content = {
                    "college_id": get_college.id,
                    "external_assessment": get_college.external_assessment,
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:

                content = {
                    "message": "College does not exist"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        elif request.method == 'POST':
            external_assessment = request.POST.get('external_assessment', None)
            try:
                external_assessment = int(external_assessment)
            except:
                external_assessment = None
            if external_assessment is None:
                content = {
                    "message": "Please provide external_assessment"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            user_details = UserDetail.objects.get(user_id=request.user.id)
            try:
                get_college = College.objects.get(id=user_details.college_id)
                get_college.external_assessment = external_assessment
                get_college.save()
                content = {
                    "message": "Updated successfully",
                    "college_id": get_college.id,
                    "external_assessment": get_college.external_assessment,
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except College.DoesNotExist:

                content = {
                    "message": "College does not exist"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college_send_otp(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        try:
            user_details = UserDetail.objects.get(
                user_id=request.user.id, college_id__isnull=False)

            otp_type = request.POST.get("otp_type", None)
            phone_number = request.POST.get("phone_number", None)
            email = request.POST.get("email", None)
            new_otp = random.randint(10000, 99999)
            name = user_details.college.college_name
            if otp_type is None or otp_type not in ["0", "1"]:
                content = {
                    "message": "Please provide otp type"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            is_otp_send = False
            if otp_type == "0" and phone_number:
                try:
                    conn = http.client.HTTPConnection(
                        "digimate.airtel.in:15181")
                    payload = json.dumps({
                        "keyword": "DEMO",
                        "timeStamp": "1659688504",
                        "dataSet": [
                            {
                                "UNIQUE_ID": "16596885049652",
                                "MESSAGE": str(
                                    name) + " has added your mobile number as the SPOC Contact for the Naan Mudhalvan program. To confirm, please use the verification code " + str(
                                    new_otp) + ".NMGOVT",
                                "OA": "NMGOVT",
                                "MSISDN": "91" + str(phone_number),
                                "CHANNEL": "SMS",
                                "CAMPAIGN_NAME": "tnega_u",
                                "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                "USER_NAME": "tnega_tnsd",
                                "DLT_TM_ID": "1001096933494158",
                                "DLT_CT_ID": "1007651074992211858",
                                "DLT_PE_ID": "1001857722001387178"
                            }
                        ]
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    conn.request(
                        "GET", "/BULK_API/InstantJsonPush", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    sms_response = data.decode("utf-8")
                    print(sms_response)
                    if sms_response == 'true':
                        is_otp_send = True
                    else:
                        is_otp_send = False
                except Exception as e:
                    content = {
                        "message": "Please provide valid data",
                        "error": str(e)
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            elif otp_type == "1" and email:
                # latest
                SMTPserver = 'mail.tn.gov.in'
                sender = 'naanmudhalvan@tn.gov.in'

                USERNAME = "naanmudhalvan"
                PASSWORD = "*nmportal2922*"
                content = f"""\
                                    Dear {name},
                
                                    Please find the OTP to update your email ID
                                            OTP : {new_otp}
                
                                    Please feel free to contact us on support email - support@naanmudhalvan.in
                
                                    Thanks,
                                    Naan Mudhalvan Team,
                                    Tamil Nadu Skill Development Corporation
                
                
                                    This is an automatically generated email from the Naan Mudhalvan Platform. Please do not reply to the sender of this email.
                                    """

                subject = "OTP from Naan Mudhalvan"
                text_subtype = 'plain'
                msg = MIMEText(content, text_subtype)
                msg['Subject'] = subject
                # some SMTP servers will do this automatically, not all
                msg['From'] = sender
                msg['Date'] = formatdate(localtime=True)

                conn = SMTP(host=SMTPserver, port=465)
                conn.set_debuglevel(False)
                conn.login(USERNAME, PASSWORD)
                try:
                    conn.sendmail(sender, [email], msg.as_string())
                    is_otp_send = True
                except ConnectionRefusedError:
                    # time.sleep(120)
                    try:
                        conn.sendmail(sender, [email], msg.as_string())
                        is_otp_send = True
                    except ConnectionRefusedError:
                        is_otp_send = False
                    except TimeoutError:
                        is_otp_send = False
                    except Exception as e:
                        is_otp_send = False
                    finally:
                        conn.quit()
                except TimeoutError:
                    # time.sleep(120)
                    try:
                        conn.sendmail(sender, [email], msg.as_string())
                        is_otp_send = True
                    except ConnectionRefusedError:
                        is_otp_send = False
                    except TimeoutError:
                        is_otp_send = False
                    except Exception as e:
                        is_otp_send = False
                    finally:
                        conn.quit()
                except Exception as e:
                    is_otp_send = False
            else:
                content = {
                    "message": "Please provide valid data"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if is_otp_send:
                new_otp_verification = CollegeOtpVerification.objects.create(
                    college_id=user_details.college_id,
                    otp_type=otp_type,
                    phone_number=phone_number,
                    email=email,
                    otp=new_otp
                )
                new_otp_verification.save()
                content = {
                    "message": "OTP sent successfully",
                    'otp_verification_id': new_otp_verification.id
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            else:
                content = {
                    "message": "Please try again later"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except UserDetail.DoesNotExist:
            content = {
                "message": "Please contact admin"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college_otp_confirmation(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        try:
            user_details = UserDetail.objects.select_related('college').get(user_id=request.user.id,
                                                                            college_id__isnull=False)
            otp_type = request.POST.get("otp_type", None)
            otp = request.POST.get("otp", None)
            try:
                otp = int(otp)
            except:
                otp = None
            if otp_type is None or otp is None:
                content = {
                    "message": "Please provide otp type/ otp"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            try:
                datetime_5_min_back = datetime.now() - timedelta(minutes=5)
                datetime_5_min_back_str = datetime_5_min_back.strftime(
                    "%Y-%m-%d %H:%M")
                otp_verification = CollegeOtpVerification.objects.filter(
                    otp_type=otp_type, college_id=user_details.college_id, is_used=False,
                    created__gte=datetime_5_min_back_str).exclude(otp=None).order_by('-created').first()

                if otp_verification:
                    if otp_verification.otp == otp:
                        get_college = user_details.college
                        # Phone Number
                        if otp_verification.otp_type == 0:
                            get_college.mobile = otp_verification.phone_number
                            get_college.save()
                            otp_verification.is_used = True
                            otp_verification.otp = None
                            otp_verification.save()
                            content = {
                                "message": "Phone number updated successfully",
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')
                        # Email
                        elif otp_verification.otp_type == 1:
                            get_college.email = otp_verification.email
                            get_college.save()
                            otp_verification.is_used = True
                            otp_verification.otp = None
                            otp_verification.save()

                            content = {
                                "message": "Email updated successfully",
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')
                        else:
                            content = {
                                "message": "Please try again later",
                            }
                            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        content = {
                            "message": "Please provide valid OTP/ OTP expired",
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                else:
                    content = {
                        "message": "Please provide valid OTP",
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            except Exception as e:
                content = {
                    "message": "Please try again later",
                    "error": str(e)
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except UserDetail.DoesNotExist:
            content = {
                "message": "Please contact admin"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def faculty(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        user_details = UserDetail.objects.select_related(
            'college').get(user_id=decoded_data['user_id'])
        college_details = user_details.college
        if request.method == 'GET':
            faculty_id = request.GET.get('faculty_id', None)
            if faculty_id is None:
                content = {
                    'message': 'faculty_id is required',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            try:
                faculty_details = CollegeFaculty.objects.get(
                    id=faculty_id, college_id=college_details.id)
                faculty_data = {
                    'id': faculty_details.id,
                    'name': faculty_details.name,
                    'email': faculty_details.email,
                    'phone_number': faculty_details.phone_number,
                    'designation': faculty_details.designation,
                    'assigned_faculty_id': faculty_details.assigned_faculty_id,
                    'details_of_skills': faculty_details.details_of_skills,
                    'highest_educational_qualification': faculty_details.highest_educational_qualification,
                    'pg_specialization': faculty_details.pg_specialization,
                    'years_of_experience': faculty_details.years_of_experience,
                    'has_master_trainer_on_honoraraium_basis': faculty_details.has_master_trainer_on_honoraraium_basis,
                    'any_relevant_certification': faculty_details.any_relevant_certification,
                    'document': faculty_details.document.url if faculty_details.document else None,

                    'branch': faculty_details.branch.name if faculty_details.branch else None,
                    'in_industry_research_others': faculty_details.in_industry_research_others,
                    'created': str(faculty_details.created),
                    'updated': str(faculty_details.updated),
                    'fdp_details': list(FacultyFDPDetails.objects.filter(faculty_id=faculty_details.id).values('id',
                                                                                                               'details',
                                                                                                               'technology'))
                }
                content = {
                    'message': 'Faculty details',
                    'data': faculty_data,
                    'status': 1
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except CollegeFaculty.DoesNotExist:
                content = {
                    'message': 'Faculty does not exist',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
        elif request.method == 'POST':
            branch_id = request.POST.get('branch_id', None)
            designation = request.POST.get('designation', None)
            name = request.POST.get('name', None)
            email = request.POST.get('email', None)
            phone_number = request.POST.get('phone_number', None)

            assigned_faculty_id = request.POST.get('assigned_faculty_id', None)
            highest_educational_qualification = request.POST.get(
                'highest_educational_qualification', None)
            pg_specialization = request.POST.get('pg_specialization', None)
            years_of_experience = request.POST.get('years_of_experience', None)
            in_industry_research_others = request.POST.get(
                'in_industry_research_others', None)
            has_master_trainer_on_honoraraium_basis = request.POST.get(
                'has_master_trainer_on_honoraraium_basis', None)
            any_relevant_certification = request.POST.get(
                'any_relevant_certification', None)
            details_of_skills = request.POST.get('details_of_skills', None)
            document = request.FILES.get('document', None)

            fdp_details = request.POST.get('fdp_details', None)
            if name is None or email is None or phone_number is None:
                content = {
                    'message': 'branch_id, designation, name, email, phone are required',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            try:
                faculty_details = CollegeFaculty.objects.create(
                    college_id=college_details.id,
                    branch_id=branch_id,
                    designation=designation,
                    name=name,
                    email=email,
                    phone_number=phone_number,

                    assigned_faculty_id=assigned_faculty_id,
                    details_of_skills=details_of_skills,
                    highest_educational_qualification=highest_educational_qualification,
                    pg_specialization=pg_specialization,
                    years_of_experience=years_of_experience,
                    in_industry_research_others=in_industry_research_others,
                    document=document,
                    has_master_trainer_on_honoraraium_basis=has_master_trainer_on_honoraraium_basis,
                    any_relevant_certification=any_relevant_certification,
                )
                faculty_details.save()
                if fdp_details is not None:
                    fdp_details = json.loads(fdp_details)
                    for fdp in fdp_details:
                        faculty_fdp_details = FacultyFDPDetails.objects.create(
                            faculty_id=faculty_details.id,
                            details=fdp['details'],
                            technology=fdp['technology']
                        )
                        faculty_fdp_details.save()
                content = {
                    'message': 'faculty has been added successfully',
                    'status': 1,
                    'data': {
                        'id': faculty_details.id,
                    }
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except Exception as e:
                return Response({
                    'message': str(e),
                    'status': 0
                }, status.HTTP_200_OK, content_type='application/json')
        elif request.method == 'PATCH':
            faculty_id = request.POST.get('faculty_id', None)
            if faculty_id is None:
                content = {
                    'message': 'faculty_id is required',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            try:
                branch_id = request.POST.get('branch_id', None)
                designation = request.POST.get('designation', None)
                name = request.POST.get('name', None)
                email = request.POST.get('email', None)
                phone_number = request.POST.get('phone_number', None)
                details_of_skills = request.POST.get('details_of_skills', None)

                assigned_faculty_id = request.POST.get(
                    'assigned_faculty_id', None)
                highest_educational_qualification = request.POST.get(
                    'highest_educational_qualification', None)
                pg_specialization = request.POST.get('pg_specialization', None)
                years_of_experience = request.POST.get(
                    'years_of_experience', None)
                in_industry_research_others = request.POST.get(
                    'in_industry_research_others', None)
                has_master_trainer_on_honoraraium_basis = request.POST.get(
                    'has_master_trainer_on_honoraraium_basis', None)
                any_relevant_certification = request.POST.get(
                    'any_relevant_certification', None)
                document = request.FILES.get('document', None)

                faculty_details = CollegeFaculty.objects.get(
                    id=faculty_id, college_id=college_details.id)
                faculty_details.branch_id = branch_id if branch_id is not None else faculty_details.branch_id
                faculty_details.designation = designation if designation is not None else faculty_details.designation
                faculty_details.name = name if name is not None else faculty_details.name
                faculty_details.email = email if email is not None else faculty_details.email
                faculty_details.phone_number = phone_number if phone_number is not None else faculty_details.phone_number

                faculty_details.details_of_skills = details_of_skills if details_of_skills is not None else faculty_details.details_of_skills
                faculty_details.assigned_faculty_id = assigned_faculty_id if assigned_faculty_id is not None else faculty_details.assigned_faculty_id
                faculty_details.highest_educational_qualification = highest_educational_qualification if highest_educational_qualification is not None else faculty_details.highest_educational_qualification
                faculty_details.pg_specialization = pg_specialization if pg_specialization is not None else faculty_details.pg_specialization
                faculty_details.pg_specialization = pg_specialization if pg_specialization is not None else faculty_details.pg_specialization
                faculty_details.years_of_experience = years_of_experience if years_of_experience is not None else faculty_details.years_of_experience
                faculty_details.in_industry_research_others = in_industry_research_others if in_industry_research_others is not None else faculty_details.in_industry_research_others
                faculty_details.has_master_trainer_on_honoraraium_basis = has_master_trainer_on_honoraraium_basis if has_master_trainer_on_honoraraium_basis is not None else faculty_details.has_master_trainer_on_honoraraium_basis
                faculty_details.any_relevant_certification = any_relevant_certification if any_relevant_certification is not None else faculty_details.any_relevant_certification

                if document:
                    faculty_details.document = document
                faculty_details.save()
                fdp_details = request.POST.get('fdp_details', None)
                if fdp_details is not None:
                    fdp_details = json.loads(fdp_details)
                    for fdp in fdp_details:
                        try:
                            faculty_fdp_details = FacultyFDPDetails.objects.get(
                                faculty_id=faculty_details.id,
                                id=fdp['id']
                            )
                            fdp['details'] = fdp['details'].strip()
                            fdp['technology'] = fdp['technology'].strip()
                            faculty_fdp_details.details = fdp['details'] if fdp[
                                'details'] is not '' else faculty_fdp_details.details
                            faculty_fdp_details.technology = fdp['technology'] if fdp[
                                'technology'] is not '' else faculty_fdp_details.technology
                            faculty_fdp_details.save()
                        except FacultyFDPDetails.DoesNotExist:
                            faculty_fdp_details = FacultyFDPDetails.objects.create(
                                details=fdp['details'],
                                technology=fdp['technology']
                            )
                            faculty_fdp_details.save()
                content = {
                    'message': 'faculty has been updated successfully',
                    'status': 1,
                    'data': {
                        'id': faculty_details.id,
                    }
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except CollegeFaculty.DoesNotExist:
                content = {
                    'message': 'Faculty does not exist',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
        elif request.method == 'DELETE':
            faculty_id = request.POST.get('faculty_id', None)
            if faculty_id is None:
                content = {
                    'message': 'faculty_id is required',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            try:

                faculty_details = CollegeFaculty.objects.get(
                    id=faculty_id, college_id=college_details.id)
                faculty_details.delete()
                content = {
                    'message': 'faculty deleted successfully',
                    'status': 1,
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except CollegeFaculty.DoesNotExist:
                content = {
                    'message': 'Faculty does not exist',
                    'status': 0
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            'message': 'You are not allowed here',
            'status': 0
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')


# get all faculties
@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def faculties(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF, ]:
        user_details = UserDetail.objects.select_related(
            'college').get(user_id=decoded_data['user_id'])
        college_details = user_details.college
        if request.method == 'GET':
            content = {
                'message': 'faculties',
                'data': list(CollegeFaculty.objects.filter(college_id=college_details.id).values('id', 'name', 'email',
                                                                                                 'phone_number',
                                                                                                 'designation',
                                                                                                 'details_of_skills',
                                                                                                 'assigned_faculty_id',
                                                                                                 'highest_educational_qualification',
                                                                                                 'pg_specialization',
                                                                                                 'years_of_experience',
                                                                                                 'in_industry_research_others',
                                                                                                 'has_master_trainer_on_honoraraium_basis',
                                                                                                 'any_relevant_certification',
                                                                                                 'created',
                                                                                                 'updated',

                                                                                                 'branch__name',).order_by('-created')),
                'status': 1
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            'message': 'You are not allowed here',
            'status': 0
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')


def get_class_list(Class):
    items = Class.__dict__.items()
    items = filter(lambda key: not key[0].startswith("_"), items)
    items = dict(items)
    return {v: str(k).replace("_", " ") for k, v in sorted(items.items(), key=lambda item: item[1])}


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def colleges_list(request):

    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        college_type = request.GET.get('college_type', None)

        query = {}
        if college_type:
            query['college_type'] = college_type
        all_colleges = College.objects.select_related(
            'affiliated_university',
            'district',
            'college_category',
        ).annotate(student_count=Count('student')).filter(**query).order_by('college_name')
        collegeTypes = get_class_list(CollegeType)
        managementTypes = get_class_list(CollegeManagementType)
        data = []
        for c in all_colleges:
            mt = managementTypes[c.management_type] if c.management_type is not None else '-'
            ct = collegeTypes[c.college_type] if c.college_type is not None else '-'
            data.append({
                'college_code': c.college_code,
                'college_name': c.college_name,
                'email': c.email,
                'mobile': c.mobile,
                'spoc_name': c.spoc_name,
                'college_type_id': c.college_type,
                'college_type': ct if ct is not None else '-',
                'affiliated_university': c.affiliated_university.name if c.affiliated_university_id is not None else '-',
                'zone': c.zone.name if c.zone is not None else '-',
                'management_type_id': c.management_type,
                'management_type': mt if mt is not None else '-',
                'year_of_establishment': c.year_of_establishment,
                'total_faculty_count': c.total_faculty_count,
                'village': c.village,
                'town_city': c.town_city,
                'district': c.district.name if c.district_id else None,
                'state': c.state,
                'pincode': c.pincode,
                'website_url': c.website_url,
                'taluk': c.taluk,
                'college_category': c.college_category.name if c.college_category_id is not None else '-',
                'principal_name': c.principal_name,
                'principal_mobile': c.principal_mobile,
                'principal_email': c.principal_email,
                'placement_name': c.placement_name,
                'placement_mobile': c.placement_mobile,
                'placement_email': c.placement_email,
                'student_count': c.student_count,
            })
        content = data
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            'message': 'You dont have the permission',
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

# API to send email to faculty

@api_view(['PATCH'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def send_email_to_faculty(request, college_id: int = 0):
    """
    if -> account_role is NM_ADMIN or NM_ADMIN_STAFF
        :param college_id
        :param request
        :return college details
    elif -> account_role COLLEGE_ADMIN or COLLEGE_ADMIN_STAFF
        :return college details

    :return:
    """
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    # print(is_send_invite)
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        user_details = UserDetail.objects.get(user_id=request.user.id)
        college_id=user_details.college_id

        try:
            faculty_id = request.data.get('faculty_id', None)
            is_send_invite = request.data.get('is_send_invite', None)
            get_faculty = CollegeFaculty.objects.get(id=faculty_id)
            get_college = College.objects.get(id=college_id)

            is_send_invite = True if is_send_invite == 'true' else False
            if is_send_invite:
                username = ''
                #
                if get_college.college_type == 2:
                    # Engineering
                    username = 'tnengg_fac' + str(get_college.college_code)
                elif get_college.college_type == 1:
                    # Arts & Science
                    username = 'tnas_fac' + str(get_college.college_code)
                elif get_college.college_type == 4:
                    username = 'tnpoly0_fac' + str(get_college.college_code)
                username = username.lower()
                password = str(random.randint(100000, 999999))
                error_message = None
                print(username)
                print(password)
                try:
                    user_info = User.objects.get(username=username)
                    user_info.set_password(password)
                    print("try saving")
                    user_info.save()
                    print(user_info)
                except User.DoesNotExist:
                    new_user = User.create_registered_user(
                        username=username,
                        college_id=college_id,
                        password=password,
                        account_role=6,
                        email=get_faculty.email,
                        mobile=get_faculty.phone_number,
                    )
                    print("except saving")
                    new_user.save()
                """
                    """
                SMTPserver = settings.CUSTOM_SMTP_HOST
                sender = settings.CUSTOM_SMTP_SENDER

                USERNAME = settings.CUSTOM_SMTP_USERNAME
                PASSWORD = settings.CUSTOM_SMTP_PASSWORD

                content = f"""\
                    Dear Team,

                    Greetings from  Naan Mudhalvan team. Thank you for your interest in Naan Mudhalvan programme

                    Please find your URL and login credentials for Naan Mudhalvan platform

                    URL to login : https://portal.naanmudhalvan.tn.gov.in/login
                                Username : {username}
                                Password : {password}

                    Please feel free to contact us on support email - support@naanmudhalvan.in

                    Thanks,
                    Naan Mudhalvan Team,
                    Tamil Nadu Skill Development Corporation


                    This is an automatically generated email from the Naan Mudhalvan Platform. Please do not reply to the sender of this email.


                    """

                subject = "Invitation to Naan Mudhalvan"
                text_subtype = 'plain'
                msg = MIMEText(content, text_subtype)
                msg['Subject'] = subject
                # some SMTP servers will do this automatically, not all
                msg['From'] = sender
                msg['Date'] = formatdate(localtime=True)

                conn = SMTP(host=SMTPserver, port=465)
                conn.set_debuglevel(False)
                conn.login(USERNAME, PASSWORD)
                is_email_sent = None
                try:
                    conn.sendmail(
                        sender, [get_faculty.email], msg.as_string())
                    is_email_sent = True
                except Exception as e:
                    print("\n\n\nSEND MAIL\n\n\n", str(e), "\n\n\n")
                    is_email_sent = False
                finally:
                    conn.quit()
                is_sms_sent = None
                if get_faculty.phone_number is not None:
                    try:
                        conn = http.client.HTTPConnection(
                            "digimate.airtel.in:15181")
                        payload = json.dumps({
                            "keyword": "DEMO",
                            "timeStamp": "1659688504",
                            "dataSet": [
                                {
                                    "UNIQUE_ID": "16596885049652",
                                    "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                    "OA": "NMGOVT",
                                    "MSISDN": "91" + str(get_faculty.phone_number),
                                    "CHANNEL": "SMS",
                                    "CAMPAIGN_NAME": "tnega_u",
                                    "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                    "USER_NAME": "tnega_tnsd",
                                    "DLT_TM_ID": "1001096933494158",
                                    "DLT_CT_ID": "1007269191406004910",
                                    "DLT_PE_ID": "1001857722001387178"
                                }
                            ]
                        })
                        headers = {
                            'Content-Type': 'application/json'
                        }

                        conn.request(
                            "GET", "/BULK_API/InstantJsonPush", payload, headers)
                        res = conn.getresponse()
                        data = res.read()
                        sms_response = data.decode("utf-8")
                        if sms_response == 'true':
                            is_sms_sent = True
                        else:
                            is_sms_sent = False
                    except Exception as e:
                        print("\n\n\nSEND SMS\n\n\n", str(e), "\n\n\n")
                        is_sms_sent = False
                # get_college.status = 1
                # get_college.save()
                content = {
                    "message": "Invitation sent successfully",
                    "data": {
                        "is_email_sent": is_email_sent,
                        "is_sms_sent": is_sms_sent,
                        'username': username,
                        'password': password
                    }
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            """ college_name = request.POST.get('college_name', None)
            college_code = request.POST.get('college_code', None)
            spoc_name = request.POST.get('spoc_name', None)
            email = request.POST.get('email', None)
            mobile = request.POST.get('mobile', None)
            zone_id = request.POST.get('zone_id', None)
            district_id = request.POST.get('district_id', None)
            pincode = request.POST.get('pincode', None)
            get_college.college_name = college_name if college_name is not None else get_college.college_name
            get_college.college_code = college_code if college_code is not None else get_college.college_code
            get_college.spoc_name = spoc_name if spoc_name is not None else get_college.spoc_name
            get_college.email = email if email is not None else get_college.email
            get_college.mobile = mobile if mobile is not None else get_college.mobile
            get_college.zone_id = zone_id if zone_id is not None else get_college.zone_id
            get_college.district_id = district_id if district_id is not None else get_college.district_id
            get_college.pincode = pincode if pincode is not None else get_college.pincode
            get_college.save() """
            #get_faculty.save()
            content = {
                "message": "Faculty details updated successfully"
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except College.DoesNotExist:
            content = {
                "message": "Faculty does not exist"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
