from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment, \
    SKillOfferingEnrollmentProgress
from django.db.models import Count
import csv
from io import StringIO
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail
from django.conf import settings
from .models import LinkPartner
from student.models import Student
from django.db.models.functions import Lower
from kp.models import KnowledgePartner
from lms.models import LMSClient
import uuid


def get_uid():
    uid = uuid.uuid4()
    uid = str(uid).replace("-", "")
    return uid[::-1]


@api_view(['GET'])
def kps(request):
    only_fs = request.GET.get('only_fs', False)
    only_fs = True if only_fs == 'true' else False
    query = {}
    if only_fs:
        query['is_fs'] = True
    return Response([{
        'id': x.id,
        'name': x.name,
        'description': x.description,
        'website': x.website,
        'logo': str('https://api.naanmudhalvan.tn.gov.in') + str(x.logo.url if x.logo else None),
    } for x in KnowledgePartner.objects.filter(**query)], status.HTTP_200_OK, content_type='application/json')


def get_secret_key(key):
    if key:
        if len(key) > 6:
            return str(key)[:3] + "*************" + str(key)[len(key)-3:]
        elif len(key) > 2:
            return str(key)[0] + "*************"
        else:
            return str(key) + "*************"
    return None


@api_view(['GET', 'POST', 'PATCH'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def kp(request, kp_id: int = None):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    if account_role == AccountRole.NM_ADMIN:
        # Details
        if request.method == 'GET' and kp_id:
            if kp_id:
                try:
                    _kp = KnowledgePartner.objects.get(id=kp_id)

                    content = {
                        # KP Details
                        "kp_id": _kp.id,
                        "name": _kp.name,
                        "enable_api": _kp.enable_api,
                        "description": _kp.description,
                        "website": _kp.website,
                        "logo": _kp.logo.url if _kp.logo else None,
                        "username": _kp.user.username if _kp.user_id else None,

                        # LMS Client details
                        'lms_client_id': _kp.lms_client_id,
                        'lms_client_key': _kp.lms_client.client_key if _kp.lms_client_id else None,
                        'client_secret': get_secret_key(_kp.lms_client.client_secret) if _kp.lms_client_id else None,
                        'lms_client_base_url': _kp.lms_client.client_base_url if _kp.lms_client_id else None,
                        'contact_name': _kp.lms_client.contact_name if _kp.lms_client_id else None,
                        'contact_phone': _kp.lms_client.contact_phone if _kp.lms_client_id else None,
                        'contact_email': _kp.lms_client.contact_email if _kp.lms_client_id else None,
                        'client': _kp.lms_client.client if _kp.lms_client_id else None,
                        # NM Client details
                        'nm_client_key': (_kp.lms_client.user.username if _kp.lms_client.user_id else None) if _kp.lms_client_id else None,

                        # Skill Offerings
                        'skill_offering_list': [
                            {
                                'skill_offering_id': skill_offering.id,
                                'course_code': skill_offering.course_code,
                                'course_name': skill_offering.course_name,
                                'mode_of_delivery': skill_offering.mode_of_delivery,
                                'duration': skill_offering.duration,
                                'outcomes': skill_offering.outcomes,
                                'course_content': skill_offering.course_content,
                                'description': skill_offering.description,
                                'certification': skill_offering.certification,
                                'cost': skill_offering.cost,
                                'link': skill_offering.link,
                                'is_mandatory': skill_offering.is_mandatory,
                                'sem': skill_offering.sem,
                                'offering_type': skill_offering.offering_type,
                                'offering_kind': skill_offering.offering_kind,
                                'job_category': skill_offering.job_category,
                                'status': skill_offering.status,
                                'ea_count': skill_offering.ea_count,
                                'ia_count': skill_offering.ia_count,
                            } for skill_offering in SKillOffering.objects.filter(
                                knowledge_partner_id=_kp.id
                            ).order_by('-id')
                        ]
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                except KnowledgePartner.DoesNotExist:
                    content = {
                        "message": "Please provide valid kp_id"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    "message": "Please provide kp_id"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        # List
        elif request.method == 'GET':
            page = request.GET.get('page', 0)
            limit = request.GET.get('limit', 20)
            search_text = request.GET.get('search_text', None)
            enable_api = request.GET.get('enable_api', None)
            try:
                page = int(page)
                limit = int(limit)
            except:
                page = 0
                limit = 20
            query = {}
            if search_text:
                query['name__istartswith'] = search_text
            if enable_api:
                try:
                    enable_api = int(enable_api)
                    query['enable_api'] = enable_api
                except:
                    enable_api = None
            knowledge_partners = KnowledgePartner.objects.filter(**query).order_by(Lower('name'))
            knowledge_partners_list = []
            for knowledge_partner in knowledge_partners[(page * limit): ((page * limit) + limit)]:
                temp_kp = {
                    "kp_id": knowledge_partner.id,
                    "name": knowledge_partner.name,
                    "enable_api": knowledge_partner.enable_api,
                    "description": knowledge_partner.description,
                    "website": knowledge_partner.website,
                    "logo": knowledge_partner.logo.url if knowledge_partner.logo else None,
                }
                knowledge_partners_list.append(temp_kp)
            content = {
                "knowledge_partners": knowledge_partners_list,
                "page": page,
                "limit": limit,
                "total_count": knowledge_partners.count() if knowledge_partners else 0
            }
            return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
        # Create
        elif request.method == 'POST':
            name = request.POST.get('name', None)
            description = request.POST.get('description', None)
            website = request.POST.get('website', None)
            logo = request.FILES.get('logo', None)
            enable_api = request.FILES.get('enable_api', None)

            lms_client_key = request.POST.get('lms_client_key', None)
            lms_client_secret = request.POST.get('lms_client_secret', None)
            lms_client_base_url = request.POST.get('lms_client_base_url', None)
            contact_email = request.POST.get('contact_email', None)
            contact_name = request.POST.get('contact_name', None)
            contact_phone = request.POST.get('contact_phone', None)

            if name is None or description is None or website is None or logo is None:
                content = {
                    "message": "Please provide name/ description/ website/ logo"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            try:
                enable_api = int(enable_api)
            except:
                enable_api = None
            new_lms = LMSClient.objects.create(client=name)
            new_kp = KnowledgePartner.objects.create(
                lms_client_id=new_lms.id,
                name=name,
                description=description,
                website=website,
                logo=logo,
                enable_api=enable_api,
            )
            new_lms = LMSClient.objects.create(
                client=new_kp.name,
                client_key=lms_client_key,
                client_secret=lms_client_secret,
                client_base_url=lms_client_base_url,
                contact_email=contact_email,
                contact_name=contact_name,
                contact_phone=contact_phone,
            )
            new_kp.lms_client_id = new_lms.id
            new_kp.save()
            content = {
                "message": "Knowledge Partner added successfully",
                "kp_id": new_kp.id
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        # Update
        elif request.method == 'PATCH':
            if kp_id:
                try:
                    _kp = KnowledgePartner.objects.get(id=kp_id)
                    name = request.POST.get('name', None)
                    description = request.POST.get('description', None)
                    website = request.POST.get('website', None)
                    logo = request.FILES.get('logo', None)
                    enable_api = request.FILES.get('enable_api', None)

                    lms_client_key = request.POST.get('lms_client_key', None)
                    lms_client_secret = request.POST.get('lms_client_secret', None)
                    lms_client_base_url = request.POST.get('lms_client_base_url', None)
                    contact_email = request.POST.get('contact_email', None)
                    contact_name = request.POST.get('contact_name', None)
                    contact_phone = request.POST.get('contact_phone', None)
                    try:
                        enable_api = int(enable_api)
                    except:
                        enable_api = None
                    _kp.name = name if name else _kp.name
                    _kp.description = description if description else _kp.description
                    _kp.website = website if website else _kp.website
                    _kp.logo = logo if logo else _kp.logo
                    _kp.enable_api = enable_api if enable_api is not None else _kp.enable_api
                    if _kp.lms_client_id:
                        _kp.lms_client.client = name if name else _kp.lms_client.client
                        _kp.lms_client.contact_email = contact_email if contact_email else _kp.lms_client.contact_email
                        _kp.lms_client.contact_name = contact_name if contact_name else _kp.lms_client.contact_name
                        _kp.lms_client.contact_phone = contact_phone if contact_phone else _kp.lms_client.contact_phone

                        _kp.lms_client.client_key = lms_client_key if lms_client_key else _kp.lms_client.client_key
                        _kp.lms_client.client_secret = lms_client_secret if lms_client_secret else _kp.lms_client.client_secret
                        _kp.lms_client.client_base_url = lms_client_base_url if lms_client_base_url else _kp.lms_client.client_base_url
                        _kp.lms_client.save()
                    else:
                        new_lms = LMSClient.objects.create(
                            client=_kp.name,
                            client_key=lms_client_key,
                            client_secret=lms_client_secret,
                            client_base_url=lms_client_base_url,
                            contact_email=contact_email,
                            contact_name=contact_name,
                            contact_phone=contact_phone,
                        )
                        _kp.lms_client_id = new_lms.id
                    _kp.save()
                    content = {
                        "message": "Knowledge Partner updated successfully",
                        "kp_id": _kp.id
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                except KnowledgePartner.DoesNotExist:
                    content = {
                        "message": "Please provide valid kp_id"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            else:
                content = {
                    "message": "Please provide kp_id"
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
def kp_user(request, kp_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    if account_role == AccountRole.NM_ADMIN:
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if username is None or password is None:
            content = {
                "message": "Please provide username/ password"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        elif str(username).strip() == "":
            content = {
                "message": "Please provide valid username"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        elif str(password).strip() == "" or len(str(password).strip()) < 8:
            content = {
                "message": "Please provide valid password with min 8 characters"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        try:
            _kp = KnowledgePartner.objects.get(id=kp_id)
            if _kp.user_id:
                content = {
                    "message": "Knowledge Partner already has a user with username:" + str(_kp.user.username)
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if User.objects.filter(username__iexact=username).exists():
                content = {
                    "message": "Username already exists"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            new_user = User.objects.create(
                username=username,
                account_role=AccountRole.KNOWLEDGE_PARTNER,
                name=_kp.name
            )
            new_user.set_password(password)
            new_user.save()
            content = {
                "message": "User created successfully",
                "username": username
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except KnowledgePartner.DoesNotExist:
            content = {
                "message": "Knowledge Partner does not exist"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST', 'PATCH'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def kp_credentials(request, kp_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    if account_role in [AccountRole.NM_ADMIN, AccountRole.KNOWLEDGE_PARTNER]:
        try:
            if account_role == AccountRole.NM_ADMIN:
                _kp = KnowledgePartner.objects.get(id=kp_id)
            else:
                _kp = KnowledgePartner.objects.get(user_id=request.user.id)
                if not _kp.enable_api:
                    context = {
                        "message": "Please contact admin to enable API"
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            if request.method == 'POST':
                if _kp.lms_client_id:
                    if _kp.lms_client.user_id:
                        context = {
                            "message": "Already created created credentials"
                        }
                        return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                else:
                    new_lms_client = LMSClient.objects.create(client=_kp.name)
                    _kp.lms_client_id = new_lms_client.id
                    _kp.save()

                new_username = get_uid()
                new_password = get_uid()
                new_user = User.objects.create(
                    username=new_username,
                    account_role=AccountRole.LMS_API_USER
                )

                new_user.set_password(new_password)
                new_user.save()
                _kp.lms_client.user_id = new_user.id
                _kp.lms_client.save()

                context = {
                    "message": "Credentials generated successfully",
                    "nm_client_key": new_username,
                    "nm_client_secret": new_password,
                }
                return Response(context, status.HTTP_200_OK, content_type='application/json')
            elif request.method == 'PATCH':
                if _kp.lms_client_id:
                    if _kp.lms_client.user_id:
                        new_password = get_uid()
                        api_user = _kp.lms_client.user
                        api_user.set_password(new_password)
                        api_user.save()

                        context = {
                            "message": "Re-generated credentials successfully",
                            "nm_client_key": api_user.username,
                            "nm_client_secret": new_password,
                        }
                        return Response(context, status.HTTP_200_OK, content_type='application/json')

                context = {
                    "message": "Please generate credentials"
                }
                return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except KnowledgePartner.DoesNotExist:
            content = {
                "message": "Please provide valid kp_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

