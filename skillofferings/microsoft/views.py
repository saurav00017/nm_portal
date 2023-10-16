from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from ..models import Specialisation, SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress, Technology, \
    SubTechnology, CourseBulkUpload
from django.db.models import Count
import csv
from io import StringIO
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail

from django.conf import settings
from student.models import Student
from datarepo.models import Branch, YearOfStudy
from lms.models import Course as LMSCourse
from kp.models import KnowledgePartner
import math
from cerberus import Validator
import yaml
import jwt
from .celery_task import async_task_microsoft_file_upload


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def upload_microsoft_file(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    skill_offering_id = request.POST.get('skill_offering_id', None)
    serial = request.POST.get('serial', None)
    csv_file = request.FILES.get('csv_file', None)
    if skill_offering_id is None or csv_file is None or serial is None:
        content = {
            "message": "Please provide skill_offering_id/ csv_file/ serial"
            }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        try:
            skill_offering = SKillOffering.objects.get(id=skill_offering_id)
            new_course_file = CourseBulkUpload.objects.create(
                skill_offering_id=skill_offering.id,
                file=csv_file,
                status=0,
                course_type=1,
                serial=serial
            )
            async_task_microsoft_file_upload.delay(new_course_file.id, serial)
            content = {
                "message": "Coursera assessment data upload initiated"
            }
            return Response(content, status=status.HTTP_200_OK)
        except SKillOffering.DoesNotExist:
            content = {
                "message": "Please provide valid skill_offering_id"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    content = {
        "message": "You dont have the permission"
    }
    return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def microsoft_file_upload_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    page = int(request.GET.get('page', 0))
    limit = int(request.GET.get('limit', 20))
    view_all = request.GET.get('view_all', None)

    query = {}
    skill_offering_id = request.GET.get('skill_offering_id', None)
    if skill_offering_id:
        query['skill_offering_id'] = skill_offering_id

    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        try:
            course_file_upload_list = CourseBulkUpload.objects.filter(**query, course_type=1).order_by('-created')
            total_count = course_file_upload_list.count()
            if view_all == '1':
                limit = total_count

            final_list = []
            for course_ in course_file_upload_list:
                temp = {
                    'course_file_upload_id': course_.id,
                    'status': course_.status,
                    'error_message': course_.error_message,
                    'created': course_.created,
                    'updated': course_.updated,
                    'skill_offering_id': course_.skill_offering_id,
                    'course_name': course_.skill_offering.course_name if course_.skill_offering_id else None,
                    'knowledge_partner_id': course_.skill_offering.knowledge_partner_id if course_.skill_offering_id else None,
                    'knowledge_partner': (course_.skill_offering.knowledge_partner.name if course_.skill_offering.knowledge_partner_id else None) if course_.skill_offering_id else None,

                }
                final_list.append(temp)

            content = {
                "upload_records": final_list,
                'filters': {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "view_all": view_all,
                    "skill_offering_id": skill_offering_id
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        except SKillOffering.DoesNotExist:
            content = {
                "message": "Please provide valid skill_offering_id"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    content = {
        "message": "You dont have the permission"
    }
    return Response(content, status=status.HTTP_400_BAD_REQUEST)

