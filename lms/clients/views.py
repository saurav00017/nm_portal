from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from cerberus import Validator
import yaml
import jwt
from django.conf import settings
from django.shortcuts import render
from django.db.models.functions import Lower
from users.models import User, AccountRole
from ..models import LMSClient, Course, CourseStatus, RecordType, StudentCourse
from django.db.models import F
from kp.models import KnowledgePartner

# Create your views here.
import uuid


def get_uid():
    uid = uuid.uuid4()
    return str(uid).replace("-", "")[::-1]


@api_view(['GET', 'POST', 'PUT'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_client(request, client_id: int = None):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        if request.method == 'GET':
            try:
                client_list = LMSClient.objects.annotate(key=F('user__username')).values(
                    'id',
                    'client_key',
                    'contact_name',
                    'contact_phone',
                    'contact_email',
                    'client',
                    'is_active',
                    'created',
                    'client_base_url',
                    'key',
                ).get(id=client_id)

                content = {
                    "client_details": dict(client_list) if client_list else None
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except Exception as e:

                content = {
                    "message": 'Please provide valid client ID'
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        elif request.method == 'POST':
            key = request.POST.get('key', None)
            secret_key = request.POST.get('secret_key', None)
            contact_name = request.POST.get('contact_name', None)
            contact_phone = request.POST.get('contact_phone', None)
            contact_email = request.POST.get('contact_email', None)
            client = request.POST.get('client', None)
            client_base_url = request.POST.get('client_base_url', None)
            request_schema = '''
                key:
                    type: string
                    empty: false
                    required: true
                secret_key:
                    type: string
                    empty: false
                    required: true
                contact_name:
                    type: string
                    empty: false
                    required: true
                contact_phone:
                    type: string
                    empty: false
                    required: true
                contact_email:
                    type: string
                    empty: false
                    required: true
                client:
                    type: string
                    empty: false
                    required: true
                client_base_url:
                    type: string
                    empty: true
                    required: false
            '''
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):

                check_key_client = LMSClient.objects.filter(client_key=key).exists()
                check_secret_key_client = LMSClient.objects.filter(client_secret=secret_key).exists()
                if check_key_client or check_secret_key_client:
                    content = {
                        "message": "Client record is already exist with key / secret key"
                    }
                    return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
                try:
                    new_client = LMSClient.objects.create(
                        client_key=key,
                        client_secret=secret_key,
                        contact_name=contact_name,
                        contact_phone=contact_phone,
                        contact_email=contact_email,
                        client=client,
                        client_base_url=client_base_url,

                    )

                    username = get_uid()
                    password = get_uid()

                    new_api_user = User.objects.create(
                        username=username,
                        email=contact_email,
                        mobile=contact_phone,
                        account_role=AccountRole.LMS_API_USER,
                    )
                    new_api_user.set_password(password)
                    new_api_user.save()
                    new_client.user_id = new_api_user.id
                    new_client.save()

                    new_kp = KnowledgePartner.objects.create(
                        lms_client_id=new_client.id,
                        name=client,
                    )

                    content = {
                        'message': "Client created successfully",
                        'KEY': username,
                        'SECRET_KEY': password,
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                except Exception as e:
                    content = {
                        'message': str(e),
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        elif request.method == 'PUT':
            key = request.POST.get('key', None)
            secret_key = request.POST.get('secret_key', None)
            secret_key = request.POST.get('secret_key', None)
            contact_name = request.POST.get('contact_name', None)
            contact_phone = request.POST.get('contact_phone', None)
            contact_email = request.POST.get('contact_email', None)
            is_active = request.POST.get('is_active', None)
            client = request.POST.get('client', None)
            client_base_url = request.POST.get('client_base_url', None)
            request_schema = '''
                key:
                    type: string
                    empty: false
                    required: true
                secret_key:
                    type: string
                    empty: false
                    required: true
                contact_name:
                    type: string
                    empty: false
                    required: true
                contact_phone:
                    type: string
                    empty: false
                    required: true
                contact_email:
                    type: string
                    empty: false
                    required: true
                client:
                    type: string
                    empty: false
                    required: true
                is_active:
                    type: string
                    empty: false
                    required: true
                client_base_url:
                    type: string
                    empty: true
                    required: false
            '''
            try:
                is_active = int(is_active)
            except:
                is_active = None
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    get_client = LMSClient.objects.get(id=client_id)
                    get_client.contact_name = contact_name if contact_name else get_client.contact_name
                    get_client.contact_email = contact_email if contact_email else get_client.contact_email
                    get_client.contact_phone = contact_phone if contact_phone else get_client.contact_phone
                    get_client.client_secret = secret_key if secret_key else get_client.client_secret
                    get_client.client_key = key if key else get_client.client_key
                    get_client.is_active = is_active if is_active else get_client.is_active
                    get_client.client = client if client else get_client.client
                    get_client.client_base_url = client_base_url if client_base_url else get_client.client_base_url

                    get_client.save()
                    content = {
                        'message': "Client successfully updated",
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                except LMSClient.DoesNotExist:
                    content = {
                        'message': 'Please provide valid client ID',
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
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_client_key_reset(request, client_id:int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        if request.method == 'POST':
            try:
                _client = LMSClient.objects.get(id=client_id)
                new_secret = get_uid()
                if _client.user_id:
                    _client.user.set_password(new_secret)
                    _client.user.save()
                else:
                    new_user = User.objects.create(
                        username=get_uid(),
                        account_role=AccountRole.LMS_API_USER
                    )
                    new_user.set_password(new_secret)
                    new_user.save()
                    _client.user = new_user
                    _client.save()
                content = {
                    'message': "Reset the secret key successfully",
                    "key": _client.user.username,
                    "secret_key": new_secret
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')


            except LMSClient.DoesNotExist:
                content = {
                    'message': "Please provide valid client id",
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            except Exception as e:
                content = {
                    'message': str(e),
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
def lms_clients(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        client_list = LMSClient.objects.values(
            'id',
            'client_key',
            'contact_name',
            'contact_phone',
            'contact_email',
            'client',
            'is_active',
            'created',
        ).all()

        content = {
            "clients_list": list(client_list) if client_list else []
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
def lms_clients_dropdown(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        client_list = LMSClient.objects.values(
            'id',
            'client',
        ).all()

        content = {
            "clients_list": list(client_list) if client_list else []
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')


    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


from ..subscription.client_api import get_api_access_key, api_subscribe, api_course_watch_url
from student.models import Student
import json
import requests


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_client_api_check(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        client_id = request.POST.get('client_id', None)
        if not client_id:
            content = {
                "message": "Please provide client_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        try:
            client = LMSClient.objects.get(id=client_id)
            course = Course.objects.filter(lms_client_id=client.id).order_by('-created').first()
            if not course:
                content = {
                    "message": "Please add a course"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            if not client.lms_dev_name:
                if not client.client_base_url or not client.client_key or not client.client_secret:
                    content = {
                        "message": "Please update client_base_url/ client_key/ client_secret"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                auth_check, access_token = get_api_access_key(client)
                if not auth_check:
                    content = {
                        "message": "Client API authentication/login failed"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            student_id = "3EA09B717DD09C6BC8B4C620E6B735A7"
            # CB-USER 5 (CBUSER05)
            student = Student.objects.get(roll_no='CBUSER05')
            student_course = StudentCourse(
                course_id=course.id,
                lms_client_id=client.id,
                student=student,
                is_mandatory=0
            )

            lms_subscribe, error_message = api_subscribe(student_course)
            access_status, access_url, error_message = api_course_watch_url(student_course)

            content = {
                "lms_subscribe": lms_subscribe,
                "subscription_error_message": error_message,
                "access_status": access_status,
                "access_url": access_url,
                "error_message": error_message,
                "message": "API integration working successfully"
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except LMSClient.DoesNotExist:
            content = {
                "message": "Please provide valid client_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:

            content = {
                "message": "Something went wrong",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


