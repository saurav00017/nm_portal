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
from ..models import Industry, Job
import random


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def job(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role == AccountRole.INDUSTRY_USER:
        job_title = request.POST.get('job_title', None)
        educational_qualification = request.POST.get('educational_qualification', None)
        start_date = request.POST.get('start_date', None)
        no_of_openings = request.POST.get('no_of_openings', None)
        last_date_of_application = request.POST.get('last_date_of_application', None)
        skills_required = request.POST.get('skills_required', None)
        salary = request.POST.get('salary', None)  # in rupee
        other_perks = request.POST.get('other_perks', None)
        job_description = request.POST.get('job_description', None)
        additional_information = request.POST.get('additional_information', None)
        location = request.POST.get('location', None)
        taluk = request.POST.get('taluk', None)
        district = request.POST.get('district', None)
        state = request.POST.get('state', None)

        request_schema = '''
                job_title:
                    type: string
                    empty: false
                    required: true
                educational_qualification:
                    type: string
                    empty: false
                    required: true
                start_date:
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
                salary:
                    type: string
                    empty: false
                    required: true
                other_perks:
                    type: string
                    empty: false
                    required: true
                job_description:
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

            new_job = Job.objects.create(
                industry_id=get_industry.id,
                job_title=job_title,
                educational_qualification=educational_qualification,
                start_date=start_date,
                no_of_openings=no_of_openings,
                last_date_of_application=last_date_of_application,
                skills_required=skills_required,
                salary=salary,
                other_perks=other_perks,
                job_description=job_description,
                additional_information=additional_information,
                location=location,
                taluk=taluk,
                district=district,
                state=state,
            )
            context = {
                "message": "Job added successfully",
                'job_id': new_job.id
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
def jobs(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.INDUSTRY_ADMIN,
                        AccountRole.INDUSTRY_STAFF,
                        AccountRole.INDUSTRY_USER]:
        job_title = request.GET.get('job_title', None)
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
        if job_title:
            try:
                query['job_title__istartswith'] = job_title
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

        job_objs = Job.objects.select_related('industry').filter(**query).order_by('-created')
        total_count = job_objs.count()
        final_jobs_list = []
        for obj in job_objs[(page* limit): ((page*limit) + limit)]:
            temp_job = {
                "industry_id": obj.industry_id,
                "industry_name": obj.industry.organisation_name if obj.industry_id else None,
                "industry_type": obj.industry.industry_type if obj.industry_id else None,

                "job_id": obj.id,
                "job_title": obj.job_title,
                "educational_qualification": obj.educational_qualification,
                "start_date": obj.start_date,
                "no_of_openings": obj.no_of_openings,
                "last_date_of_application": obj.last_date_of_application,
                "skills_required": obj.skills_required,
                "salary": obj.salary,
                "other_perks": obj.other_perks,
                "job_description": obj.job_description,
                "additional_information": obj.additional_information,
                "location": obj.location,
                "taluk": obj.taluk,
                "district": obj.district,
                "state": obj.state,
                "created": obj.created,
            }
            final_jobs_list.append(temp_job)
        context = {
            "internships": final_jobs_list,
            "filters": {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'internship_title': job_title,
                'industry_id': industry_id,
            }
        }
        return Response(context, status.HTTP_200_OK, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


