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
def student_placement_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        sem = request.GET.get('sem', None)
        branch_id = request.GET.get('branch_id', None)

        query = {}
        if sem:
            query['sem'] = sem
        if branch_id:
            query['rbranch_id'] = branch_id

        page = request.GET.get('page', 0)
        limit = request.GET.get('limit', 20)
        try:
            page = int(page)
            limit = int(limit)
        except:
            page = 0
            limit = 20

        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            college_id = user_details.college_id
            get_student = Student.objects.filter(college_id=college_id, **query)
            data = []
            is_placement = None
            for item in get_student[(page * limit): (page * limit) + limit]:
                try:
                    student_info = StudentPlacementDetail.objects.get(student_id=item.id)
                    is_placement = True
                except StudentPlacementDetail.DoesNotExist:
                    is_placement = False
                temp = {
                    'student_id': item.id,
                    'student_name': item.first_name + item.last_name,
                    'phone_number': item.phone_number,
                    'branch_id': item.rbranch_id,
                    'branch_name': item.rbranch.name,
                    'sem': item.sem,
                    'roll_no': item.roll_no,
                    'is_placement': is_placement
                }
                data.append(temp)
            context = {
                'data': data,
                'page': page,
                'limit': limit,
                'count': get_student.count()
            }
            return Response(context, status.HTTP_200_OK, content_type='application/json')
        except UserDetail.DoesNotExist:
            content = {
                "message": "Record not found"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
