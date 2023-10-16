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
from ..models import Industry, Internship
import random


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def internship(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role == AccountRole.INDUSTRY_USER:
        internship_title = request.POST.get('internship_title', None)
        internship_type = request.POST.get('internship_type', None)
        eligible_criteria = request.POST.get('eligible_criteria', None)
        start_date = request.POST.get('start_date', None)
        duration = request.POST.get('duration', None)
        no_of_openings = request.POST.get('no_of_openings', None)
        last_date_of_application = request.POST.get('last_date_of_application', None)
        skills_required = request.POST.get('skills_required', None)
        free_or_paid = request.POST.get('free_or_paid', None)
        stipend_details = request.POST.get('stipend_details', None)
        other_perks = request.POST.get('other_perks', None)
        about_internship = request.POST.get('about_internship', None)
        additional_information = request.POST.get('additional_information', None)
        location = request.POST.get('location', None)
        taluk = request.POST.get('taluk', None)
        district = request.POST.get('district', None)
        state = request.POST.get('state', None)

        request_schema = '''
                internship_title:
                    type: string
                    empty: false
                    required: true
                internship_type:
                    type: string
                    empty: false
                    required: true
                eligible_criteria:
                    type: string
                    empty: false
                    required: true
                start_date:
                    type: string
                    empty: false
                    required: true
                duration:
                    type: string
                    empty: false
                    required: true
                no_of_openings:
                    type: string
                    empty: false
                    required: true
                last_date_of_application:
                    type: string
                    empty: false
                    required: true
                skills_required:
                    type: string
                    empty: false
                    required: true
                free_or_paid:
                    type: string
                    empty: false
                    required: true
                stipend_details:
                    type: string
                    empty: false
                    required: true
                other_perks:
                    type: string
                    empty: false
                    required: true
                about_internship:
                    type: string
                    empty: false
                    required: true
                additional_information:
                    type: string
                    empty: false
                    required: true
                location:
                    type: string
                    empty: false
                    required: true
                taluk:
                    type: string
                    empty: false
                    required: true
                district:
                    type: string
                    empty: false
                    required: true
                state:
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

            new_internship = Internship.objects.create(
                industry_id=get_industry.id,
                internship_title=internship_title,
                internship_type=internship_type,
                eligible_criteria=eligible_criteria,
                start_date=start_date,
                duration=duration,
                no_of_openings=no_of_openings,
                last_date_of_application=last_date_of_application,
                skills_required=skills_required,
                free_or_paid=free_or_paid,
                stipend_details=stipend_details,
                other_perks=other_perks,
                about_internship=about_internship,
                additional_information=additional_information,
                location=location,
                taluk=taluk,
                district=district,
                state=state,
            )
            context = {
                "message": "Internship added successfully",
                'internship_id': new_internship.id
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
def internships(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.INDUSTRY_ADMIN,
                        AccountRole.INDUSTRY_STAFF,
                        AccountRole.INDUSTRY_USER]:
        internship_title = request.GET.get('internship_title', None)
        internship_type = request.GET.get('internship_type', None)  # 0 - virtual, 1 - in-person
        industry_id = request.GET.get('industry_id', None)
        free_or_paid = request.GET.get('free_or_paid', None)  # 0 - free, 1 - paid
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
        if internship_title:
            try:
                query['internship_title__istartswith'] = internship_title
            except:
                pass

        if internship_type:
            try:
                query['internship_type'] = int(internship_type)
            except:
                pass
        if free_or_paid:
            try:
                query['free_or_paid'] = int(free_or_paid)
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

        internship_objs = Internship.objects.select_related('industry').filter(**query).order_by('-created')
        total_count = internship_objs.count()
        final_internship_list = []
        for obj in internship_objs[(page* limit): ((page*limit) + limit)]:
            temp_internship = {
                "industry_id": obj.industry_id,
                "industry_name": obj.industry.organisation_name if obj.industry_id else None,
                "industry_type": obj.industry.industry_type if obj.industry_id else None,

                "internship_id": obj.id,
                "internship_title": obj.internship_title,
                "internship_type": obj.internship_type,
                "eligible_criteria": obj.eligible_criteria,
                "start_date": obj.start_date,
                "duration": obj.duration,
                "no_of_openings": obj.no_of_openings,
                "last_date_of_application": obj.last_date_of_application,
                "skills_required": obj.skills_required,
                "free_or_paid": obj.free_or_paid,
                "stipend_details": obj.stipend_details,
                "other_perks": obj.other_perks,
                "about_internship": obj.about_internship,
                "additional_information": obj.additional_information,
                "location": obj.location,
                "taluk": obj.taluk,
                "district": obj.district,
                "state": obj.state,
                "created": obj.created,
            }
            final_internship_list.append(temp_internship)
        context = {
            "internships": final_internship_list,
            "filters": {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'internship_title': internship_title,
                'internship_type': internship_type,
                'free_or_paid': free_or_paid,
                'industry_id': industry_id,
            }
        }
        return Response(context, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


