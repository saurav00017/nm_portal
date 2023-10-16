from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail
from lms.models import LMSClient, Course, CourseStatus, StudentCourse, RecordType, CourseHistory

from django.conf import settings
from lms.subscription.client_api import api_subscribe, api_course_watch_url
from django.db import transaction as atomic_transaction


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_launch_access_url(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if account_role == AccountRole.STUDENT:
        course_id = request.POST.get('course_id', None)
        try:
            course_id = int(course_id)
        except:
            course_id = None
        if course_id:
            try:
                get_profile = UserDetail.objects.select_related('student').get(user_id=request.user.id)
                get_course = Course.objects.get(
                    id=course_id)
                try:
                    check_student_subscription = StudentCourse.objects.get(
                        course_id=get_course.id,
                        student_id=get_profile.student_id)
                except StudentCourse.DoesNotExist:
                    new_subscription = StudentCourse.objects.create(
                        student_id=get_profile.student_id,
                        course_id=get_course.id,
                        lms_client_id=get_course.lms_client_id,
                    )
                    lms_subscribe, error_message = api_subscribe(new_subscription)
                    if lms_subscribe:

                        access_status, access_url, error_message = api_course_watch_url(new_subscription)
                        if access_status:
                            content = {
                                'watch_url': access_url,
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')
                        else:
                            content = {
                                'message': "KP - " + str(error_message),
                                "access_status": access_status
                            }
                            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        content = {
                            'message': "Please try again later",
                            'subscription_status': lms_subscribe
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except StudentCourse.MultipleObjectsReturned:

                    check_student_subscriptions = StudentCourse.objects.filter(
                        course_id=get_course.id,
                        student_id=get_profile.student_id)

                    check_student_subscription = check_student_subscriptions.first()
                    for record in check_student_subscriptions.exclude(id=check_student_subscription.id):
                        record.delete()
                access_status, access_url, error_message = api_course_watch_url(check_student_subscription)
                if access_status:
                    content = {
                        'watch_url': access_url,
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                else:
                    content = {
                        'message': "KP - " + str(error_message),
                        "access_status": access_status
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            except Exception as e:
                content = {
                    'message': "Please try again",
                    "error": str(e),
                    "1": True
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "Please provide course id",
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "You dont have a permission",
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

