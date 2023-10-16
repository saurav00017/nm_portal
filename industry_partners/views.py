from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
import yaml
from datarepo.models import AccountRole
from users.models import User
from .models import Industry
import random
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText
from email.utils import formatdate
import time

@api_view(['POST'])
def industry_registration(request):

    organisation_name = request.POST.get('organisation_name', None)
    industry_type = request.POST.get('industry_type', None)
    address = request.POST.get('address', None)
    contact_1_name = request.POST.get('contact_1_name', None)
    contact_1_email = request.POST.get('contact_1_email', None)
    contact_1_phone_number = request.POST.get('contact_1_phone_number', None)
    contact_2_name = request.POST.get('contact_2_name', None)
    contact_2_email = request.POST.get('contact_2_email', None)
    contact_2_phone_number = request.POST.get('contact_2_phone_number', None)
    has_internships = request.POST.get('has_internships', None)
    has_job_openings = request.POST.get('has_job_openings', None)
    industry_speaks = request.POST.get('industry_speaks', None)

    internship_poc_name = request.POST.get('internship_poc_name', None)
    internship_poc_email = request.POST.get('internship_poc_email', None)
    internship_poc_phone_number = request.POST.get('internship_poc_phone_number', None)

    job_poc_name = request.POST.get('job_poc_name', None)
    job_poc_email = request.POST.get('job_poc_email', None)
    job_poc_phone_number = request.POST.get('job_poc_phone_number', None)

    if has_internships:
        try:
            has_internships = int(has_internships)
        except:
            has_internships = False
    if has_job_openings:
        try:
            has_job_openings = int(has_job_openings)
        except:
            has_job_openings = False
    request_schema = '''
            organisation_name:
                type: string
                empty: false
                required: true
            industry_type:
                type: string
                empty: false
                required: true
            address:
                type: string
                empty: false
                required: true
            contact_1_name:
                type: string
                empty: false
                required: true
            contact_1_email:
                type: string
                empty: false
                required: true
            contact_1_phone_number:
                type: string
                empty: false
                required: true
            contact_2_name:
                type: string
                empty: true
                required: false
            contact_2_email:
                type: string
                empty: true
                required: false
            contact_2_phone_number:
                type: string
                empty: true
                required: false
            has_internships:
                type: string
                empty: false
                required: true
                min: 1
                max: 1
            has_job_openings:
                type: string
                empty: false
                required: true
                min: 1
                max: 1
            industry_speaks:
                type: string
                empty: false
                required: true
            internship_poc_name:
                type: string
                empty: true
                required: false
            internship_poc_email:
                type: string
                empty: true
                required: false
            internship_poc_phone_number:
                type: string
                empty: true
                required: false
            job_poc_name:
                type: string
                empty: true
                required: false
            job_poc_email:
                type: string
                empty: true
                required: false
            job_poc_phone_number:
                type: string
                empty: true
                required: false
            '''
    v = Validator()
    post_data = request.POST.dict()
    schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
    if v.validate(post_data, schema):
        new_industry = Industry.objects.create(
            organisation_name=organisation_name,
            industry_type=industry_type,
            address=address,
            contact_1_name=contact_1_name,
            contact_1_email=contact_1_email,
            contact_1_phone_number=contact_1_phone_number,
            contact_2_name=contact_2_name,
            contact_2_email=contact_2_email,
            contact_2_phone_number=contact_2_phone_number,
            has_internships=has_internships,
            has_job_openings=has_job_openings,
            industry_speaks=industry_speaks,

            internship_poc_name=internship_poc_name,
            internship_poc_email=internship_poc_email,
            internship_poc_phone_number=internship_poc_phone_number,

            job_poc_name=job_poc_name,
            job_poc_email=job_poc_email,
            job_poc_phone_number=job_poc_phone_number,
        )
        context = {
            "message": "Request sent for approval successfully",
            'industry_id': new_industry.id
        }
        return Response(context, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            'message': "invalid request",
            'errors': v.errors
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')



@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def industries(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    industry_status = request.GET.get('industry_status', None)
    organisation_name = request.GET.get('organisation_name', None)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    if industry_status:
        try:
            industry_status = int(industry_status)
            query['status'] = industry_status
        except:
            industry_status = None
    if organisation_name:
        query['organisation_name__istartswith'] = organisation_name

    if account_role in [AccountRole.NM_ADMIN, AccountRole.INDUSTRY_ADMIN, AccountRole.INDUSTRY_STAFF]:
        industry_objs = Industry.objects.filter(**query).order_by('-created')
        final_industry_list = []
        total_count = industry_objs.count()
        for industry_obj in industry_objs[(page * limit): ((page*limit) + limit)]:
            temp_industry = {
                'industry_id': industry_obj.id,
                'organisation_name': industry_obj.organisation_name,
                'industry_type': industry_obj.industry_type,
                'address': industry_obj.address,
                'contact_1_name': industry_obj.contact_1_name,
                'contact_1_email': industry_obj.contact_1_email,
                'contact_1_phone_number': industry_obj.contact_1_phone_number,
                'contact_2_name': industry_obj.contact_2_name,
                'contact_2_email': industry_obj.contact_2_email,
                'contact_2_phone_number': industry_obj.contact_2_phone_number,
                'has_internships': industry_obj.has_internships,
                'internship_poc_name': industry_obj.internship_poc_name,
                'internship_poc_email': industry_obj.internship_poc_email,
                'internship_poc_phone_number': industry_obj.internship_poc_phone_number,
                'has_job_openings': industry_obj.has_job_openings,
                'job_poc_name': industry_obj.job_poc_name,
                'job_poc_email': industry_obj.job_poc_email,
                'job_poc_phone_number': industry_obj.job_poc_phone_number,
                'industry_speaks': industry_obj.industry_speaks,
                'status': industry_obj.status,
                'created': industry_obj.created,
                'updated': industry_obj.updated,
            }
            final_industry_list.append(temp_industry)

        content = {
            "industries": final_industry_list,
            'filters': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'industry_status': industry_status,
                'organisation_name': organisation_name,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def industry(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    industry_id = request.POST.get('industry_id', None)
    industry_status = request.POST.get('industry_status', None)
    try:
        industry_id = int(industry_id)
        industry_status = int(industry_status)
    except:
        industry_id = None
        industry_status = None

    if industry_id is None or industry_status is None:
        content = {
            "message": "Please provide industry id/ industry status"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.NM_ADMIN, AccountRole.INDUSTRY_ADMIN, AccountRole.INDUSTRY_STAFF]:
        get_industry = Industry.objects.get(id=industry_id)
        if get_industry.status == 0:
            get_industry.status = industry_status
            username = None
            password = None
            send_mail = False
            if get_industry.status == 1 and get_industry.contact_1_email:
                username = get_industry.contact_1_email
                password = random.randint(100000, 999999)
                send_mail = True
                try:
                    check_user = User.objects.get(username=username)
                    username = username + str(random.randint(0,9))
                except:
                    pass
                new_user = User.objects.create(
                    username=username, email=get_industry.contact_1_email,
                    account_role=AccountRole.INDUSTRY_USER
                )
                new_user.set_password(str(password))
                new_user.save()
                get_industry.user_id = new_user.id

                """
                Email Code
                """

            get_industry.save()
            emails_list = []
            if get_industry.contact_1_email is not None and get_industry.contact_1_email!="":
                emails_list.append(get_industry.contact_1_email)
            if get_industry.contact_2_email is not None and get_industry.contact_2_email!="":
                emails_list.append(get_industry.contact_2_email)
            if send_mail:
                organisation_name = get_industry.organisation_name
                try:
                    # latest
                    SMTPserver = 'mail.tn.gov.in'
                    sender = 'naanmudhalvan@tn.gov.in'

                    USERNAME = "naanmudhalvan"
                    PASSWORD = "*nmportal2922*"
                    content = f"""\
                                Dear {organisation_name},
            
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
                    msg['From'] = sender  # some SMTP servers will do this automatically, not all
                    msg['Date'] = formatdate(localtime=True)

                    conn = SMTP(host=SMTPserver, port=465)
                    conn.set_debuglevel(False)
                    conn.login(USERNAME, PASSWORD)
                    try:
                        conn.sendmail(sender, emails_list, msg.as_string())
                        get_industry.has_mailed = True
                        get_industry.save()
                    except ConnectionRefusedError:
                        time.sleep(0.1)
                        try:
                            conn.sendmail(sender, emails_list, msg.as_string())
                            get_industry.has_mailed = True
                            get_industry.save()
                        except ConnectionRefusedError:
                            print("Industry Sending Email - ConnectionRefusedError")
                        except TimeoutError:
                            print("Industry Sending Email - TimeoutError")
                        except Exception as e:
                            print("Industry Sending Email -", e)

                except Exception as e:
                    print("Industry Sending Email Failed", e)

            content = {
                "message": "updated successfully",
                'username': username,
                'password': password,
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        else:
            content = {
                "message": "Already updated",
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

