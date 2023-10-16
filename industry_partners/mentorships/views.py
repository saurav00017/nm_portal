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
from ..models import Industry, Mentorship
import random


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def mentorship(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role == AccountRole.INDUSTRY_USER:
        mentor_name = request.POST.get('mentor_name', None)
        mentor_email = request.POST.get('mentor_email', None)
        mentor_phone_number = request.POST.get('mentor_phone_number', None)
        designation = request.POST.get('designation', None)
        availability = request.POST.get('availability', None)
        mode = request.POST.get('mode', None)
        linkedin_profile_url = request.POST.get('linkedin_profile_url', None)  # in rupee
        languages = request.POST.get('languages', None)

        request_schema = '''
                mentor_name:
                    type: string
                    empty: false
                    required: true
                mentor_email:
                    type: string
                    empty: false
                    required: true
                mentor_phone_number:
                    type: string
                    empty: false
                    required: true
                designation:
                    type: string
                    empty: false
                    required: true
                availability:
                    type: string
                    empty: false
                    required: true
                mode:
                    type: string
                    empty: false
                    required: true
                linkedin_profile_url:
                    type: string
                    empty: false
                    required: true
                languages:
                    type: string
                    empty: false
                    required: true
                '''
        v = Validator()
        post_data = request.POST.dict()
        schema = yaml.load(request_schema, Loader=yaml.SafeLoader)

        if v.validate(post_data, schema):
            try:
                get_industry = Industry.objects.get(user_id=request.user.id)
            except Industry.DoesNotExist:
                content = {
                    "message": "Please contact admin"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            new_mentorship = Mentorship.objects.create(
                industry_id=get_industry.id,
                mentor_name=mentor_name,
                mentor_email=mentor_email,
                mentor_phone_number=mentor_phone_number,
                designation=designation,
                availability=availability,
                mode=mode,
                linkedin_profile_url=linkedin_profile_url,
                languages=languages,
            )
            context = {
                "message": "Mentorship added successfully",
                'mentorship_id': new_mentorship.id
            }
            return Response(context, status.HTTP_200_OK, content_type='application/json')

        else:
            content = {
                'message': "invalid request",
                'errors': v.errors
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def mentorships(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.INDUSTRY_ADMIN,
                        AccountRole.INDUSTRY_STAFF,
                        AccountRole.INDUSTRY_USER]:
        industry_id = request.GET.get('industry_id', None)
        page = request.GET.get('page', 0)
        limit = request.GET.get('limit', 20)
        try:
            page = int(page)
            limit = int(limit)
        except:
            page = 0
            limit = 20

        query = {}
        if industry_id:
            try:
                query['industry_id'] = int(industry_id)
            except:
                pass

        if account_role == AccountRole.INDUSTRY_USER:
            try:
                get_industry = Industry.objects.values('id').get(user_id=request.user.id)
                query['industry_id'] = get_industry['id']
            except Industry.DoesNotExist:
                content = {
                    "message": "Please contact admin"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        mentors_objs = Mentorship.objects.select_related('industry').filter(**query).order_by('-created')
        total_count = mentors_objs.count()
        final_mentors_list = []
        for obj in mentors_objs[(page* limit): ((page*limit) + limit)]:
            temp = {
                "industry_id": obj.industry_id,
                "industry_name": obj.industry.organisation_name if obj.industry_id else None,
                "industry_type": obj.industry.industry_type if obj.industry_id else None,

                "mentorship_id": obj.id,
                "mentor_name": obj.mentor_name,
                "mentor_email": obj.mentor_email,
                "mentor_phone_number": obj.mentor_phone_number,
                "designation": obj.designation,
                "availability": obj.availability,
                "mode": obj.mode,
                "linkedin_profile_url": obj.linkedin_profile_url,
                "languages": obj.languages,
                "created": obj.created,
            }
            final_mentors_list.append(temp)
        context = {
            "mentors": final_mentors_list,
            "filters": {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'industry_id': industry_id,
            }
        }
        return Response(context, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


