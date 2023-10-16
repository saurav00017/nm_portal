from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from ..models import Specialisation, SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress, Technology, \
    SubTechnology, FeedBack, MandatoryCourse
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


@api_view(['POST', 'PATCH', 'GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def nm_mandatory_course(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    if account_role == AccountRole.NM_ADMIN:
        mandatory_course_id = request.POST.get('mandatory_course_id', None)
        college_id = request.POST.get('college_id', None)
        skill_offering_id = request.POST.get('skill_offering_id', None)
        course_type = request.POST.get('course_type', None)
        is_unlimited = request.POST.get('is_unlimited', None)
        branch_id = request.POST.get('branch_id', None)
        sem = request.POST.get('sem', None)
        count = request.POST.get('count', None)
        if request.method == 'GET':
            mandatory_course_id = request.GET.get('mandatory_course_id', None)
            try:
                mc_record = MandatoryCourse.objects.get(
                    mandatory_course_id=mandatory_course_id
                )

                context = {
                    'mandatory_course_id': mc_record.id,
                    'college': mc_record.college.college_name if mc_record.college_id else None,
                    'college_code': mc_record.college.college_code if mc_record.college_id else None,
                    'skill_offering_id': mc_record.skill_offering_id if mc_record.skill_offering_id else None,
                    'course': mc_record.skill_offering.course_name if mc_record.skill_offering_id else None,
                    'course_type': mc_record.course_type,
                    'is_unlimited': mc_record.is_unlimited,
                    'branch_id': mc_record.branch.id if mc_record.branch_id else None,
                    'branch': mc_record.branch.name if mc_record.branch_id else None,
                    'sem': mc_record.sem,
                    'count': mc_record.count,
                    'created': mc_record.created,
                    'updated': mc_record.updated,
                }
                return Response(context, status.HTTP_200_OK, content_type='application/json')
            except MandatoryCourse.DoesNotExist:
                context = {
                    'message': "Please provide mandatory_course_id",
                }
                return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        elif request.method == 'POST':
            if college_id is None or skill_offering_id is None or course_type is None or is_unlimited is None or branch_id is None or sem is None \
                    or count is None:
                context = {
                    'message': "Please provide college_id/ skill_offering_id/ course_type/ is_unlimited/ branch_id/ sem/ count",
                }
                return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            mc_record = MandatoryCourse.objects.filter(
                college_id=college_id,
                skill_offering_id=skill_offering_id,
                branch_id=branch_id,
                sem=sem,
            ).exists()
            if mc_record:
                context = {
                    'message': "Mandatory Course already exists",
                }
                return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                mc_record = MandatoryCourse.objects.create(
                    college_id=college_id,
                    skill_offering_id=skill_offering_id,
                    is_unlimited=is_unlimited,
                    course_type=course_type,
                    branch_id=branch_id,
                    sem=sem,
                    count=count
                )
                context = {
                    'message': "Added successfully",
                }
                return Response(context, status.HTTP_200_OK, content_type='application/json')
        elif request.method == 'PATCH':
            if mandatory_course_id is None:
                context = {
                    'message': "Please provide mandatory_course_id",
                }
                return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            try:
                mc_record = MandatoryCourse.objects.get(
                    id=mandatory_course_id
                )
                mc_record.is_unlimited = is_unlimited if is_unlimited else mc_record.is_unlimited
                mc_record.course_type = course_type if course_type else mc_record.course_type
                mc_record.count = count if count else mc_record.count
                mc_record.save()
                context = {
                    'message': "updated successfully",
                }
                return Response(context, status.HTTP_200_OK, content_type='application/json')
            except MandatoryCourse.DoesNotExist:
                context = {
                    'message': "Please provide valid mandatory_course_id",
                }
                return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def nm_mandatory_course_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if account_role == AccountRole.NM_ADMIN:
        page = int(request.GET.get('page', 0))
        limit = int(request.GET.get('limit', 20))
        college_id = request.GET.get('college_id', None)
        skill_offering_id = request.GET.get('skill_offering_id', None)
        course_type = request.GET.get('course_type', None)
        is_unlimited = request.GET.get('is_unlimited', None)
        branch_id = request.GET.get('branch_id', None)
        sem = request.GET.get('sem', None)

        mc_list = MandatoryCourse.objects.filter().order_by('-created')
        total_count = mc_list.count()
        final_list = []
        for mc_record in mc_list[(page * limit): ((page * limit) + limit)]:
            temp = {
                'mandatory_course_id': mc_record.id,
                'college': mc_record.college.college_name if mc_record.college_id else None,
                'college_code': mc_record.college.college_code if mc_record.college_id else None,
                'skill_offering_id': mc_record.skill_offering_id if mc_record.skill_offering_id else None,
                'course': mc_record.skill_offering.course_name if mc_record.skill_offering_id else None,
                'course_type': mc_record.course_type,
                'is_unlimited': mc_record.is_unlimited,
                'branch_id': mc_record.branch.id if mc_record.branch_id else None,
                'branch': mc_record.branch.name if mc_record.branch_id else None,
                'sem': mc_record.sem,
                'count': mc_record.count,
                'created': mc_record.created,
                'updated': mc_record.updated,
            }
            final_list.append(temp)
        content = {
            'mandatory_courses': final_list,
            'filters': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'college_id': college_id,
                'skill_offering_id': skill_offering_id,
                'course_type': course_type,
                'is_unlimited': is_unlimited,
                'branch_id': branch_id,
                'sem': sem,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')

    else:
        return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
