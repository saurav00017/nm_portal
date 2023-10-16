from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from datarepo.models import AccountRole
from users.models import User, UserDetail
from student.models import Student
from placements.models import StudentPlacementDetail


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def placement_overview(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF, AccountRole.SUPER_ADMIN]:
        student_placement_info = StudentPlacementDetail.objects.filter(student__college__college_type=2,student__sem__in=[7,8])
        engineering = {
            'entrepreneurship_count': student_placement_info.filter(current_status='Entrepreneurship').count(),
            'received_job_offers_count': student_placement_info.filter(current_status='Received Job offer').count(),
            'preparing_for_competitive_exams_count': student_placement_info.filter(
                current_status='Preparing for Competitive Exams').count(),
            'looking_for_job_count': student_placement_info.filter(current_status='Looking for a Job').count(),
            'planning_for_higher_education_count': student_placement_info.filter(
                current_status='Planning for Higher Education').count(),
            'final_year_students_count': student_placement_info.count()
        }
        student_placement_info = StudentPlacementDetail.objects.filter(student__college__college_type=1,student__sem__in=[6, 7])
        arts = {
            'entrepreneurship_count': student_placement_info.filter(current_status='Entrepreneurship').count(),
            'received_job_offers_count': student_placement_info.filter(current_status='Received Job offer').count(),
            'preparing_for_competitive_exams_count': student_placement_info.filter(
                current_status='Preparing for Competitive Exams').count(),
            'looking_for_job_count': student_placement_info.filter(current_status='Looking for a Job').count(),
            'planning_for_higher_education_count': student_placement_info.filter(
                current_status='Planning for Higher Education').count(),
            'final_year_students_count': student_placement_info.count()
        }
        return Response({
            'engineering': engineering,
            'arts': arts
        }, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
