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
from ..models import LMSClient, Course, CourseStatus, RecordType, CourseHistory, StudentCourse
from django.db.models import F
from datarepo.views import get_class_list
# Create your views here.
import uuid

from django.conf import settings
from django.template.loader import get_template
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from nm_portal.config import Config
from kp.models import KnowledgePartner
from skillofferings.models import SKillOffering

def send_mail_to_client(to_mail, course: Course, course_status):
    """
    Send email to customer with order details.
    """
    message = ''
    message_content = ''
    print('to_mail', to_mail)
    print('course', course)
    print('course_status', course_status)
    if course_status == CourseStatus.APPROVED:

        message = 'Course has approved from the Naan Mudhalvan team. Details of course as shown below table'
        message_content = get_template("emails/course_update.html").render({'message': message, 'course': course})

    elif course_status == CourseStatus.REJECTED:
        message = 'Course has approved from the Naan Mudhalvan team. Details of course as shown below table'
        message_content = get_template("emails/course_update.html").render({'message': message, 'course': course})
    try:
        FROM_EAMIL = 'chandumanikumar4@gmail.com'
        mail = EmailMultiAlternatives(
            subject="Course update | Naan Mudhalvan",
            body=message_content,
            from_email=FROM_EAMIL,
            to=[to_mail],
            reply_to=[FROM_EAMIL],
        )
        mail.content_subtype = "html"
        mail.mixed_subtype = 'related'
        mail.attach_alternative(message, "text/html")
        # mail.content_subtype = "html"
        send = mail.send()
        return 1
    except Exception as e:
        print(e)
        return 0


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_courses(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20
    query = {}

    name = request.GET.get('name', None)
    if name:
        query['name__istartswith'] = name
    course_unique_code = request.GET.get('course_unique_code', None)
    if course_unique_code:
        query['course_unique_code'] = course_unique_code
    is_active = request.GET.get('is_active', None)
    if is_active in ['0', '1']:
        query['is_active'] = int(is_active)
    client_status = request.GET.get('client_status', None)
    if client_status in ['0', '1']:
        query['client_status'] = int(client_status)

    course_status = request.GET.get('status', None)
    if course_status:
        query['status'] = int(course_status)

    course_type = request.GET.get('course_type', None)
    if course_type:
        query['course_type'] = course_type
    category = request.GET.get('category', None)
    if category:
        query['category'] = category
    language = request.GET.get('language', None)
    if language:
        query['language'] = language
    sub_stream = request.GET.get('sub_stream', None)
    if sub_stream:
        query['sub_stream__icontains'] = sub_stream

    lms_client_id = request.GET.get('lms_client_id', None)
    if lms_client_id:
        try:
            query['lms_client_id'] = int(lms_client_id)
        except:
            pass

    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        pass
    else:
        query['status'] = CourseStatus.APPROVED
    courses_count = Course.objects.filter(**query).count()

    courses_list = Course.objects.annotate(
        lms_client_name=F('lms_client__client'),
        approved_user=F('approved_by__username')
    ).values(
        'id',
        'course_unique_code',
        'course_name',
        'course_type',
        'location',
        'course_description',
        'course_content',
        'course_objective',
        'course_image_url',
        'partner_name',
        'category',
        'instructor',
        'duration',
        'number_of_videos',
        'language',
        'sub_stream',
        # 'course_outcomes',
        'system_requirements',
        'has_subtitles',
        'reference_id',
        'is_active',
        'client_status',
        'status',
        'is_active',
        'approved_user',
        'lms_client_name',
        'lms_client_id',
        'created',
        'updated',
    ).filter(**query).order_by('-created')[(page * limit): ((page * limit) + limit)]
    courses_list = list(courses_list)
    final_course_list = []
    for course in courses_list:
        course_history_query = {}
        if course['status'] == CourseStatus.NEW:
            course_history_query['record_type'] = RecordType.NEW

        course_history_record = CourseHistory.objects.values(
            'id',
            'record_type',
            'status',
        ).filter(
            course_id=course['id'], **course_history_query
        ).order_by('-created').first()

        temp_course = {
            **course,
            'course_history_id': course_history_record['id'] if course_history_record else None,
            'course_history_record_type': course_history_record['record_type'] if course_history_record else None,
            'course_history_status': course_history_record['status'] if course_history_record else None,
        }
        if account_role == AccountRole.STUDENT:
            student_course = StudentCourse.objects.filter(student__profile_student__user_id=request.user.id, course_id=course['id']).first()
            temp_course['is_subscribed'] = True if student_course else False
            temp_course['progress'] = {
                'progress_percentage': student_course.progress_percentage,
                'assessment_status': student_course.assessment_status,
                'course_complete': student_course.course_complete,
                'certificate_issued': student_course.certificate_issued,
                'certificate_issued_at': student_course.certificate_issued_at,
            } if student_course else None
        final_course_list.append(temp_course)

    content = {
        "courses_list": list(final_course_list) if final_course_list else [],
        'page': page,
        'limit': limit,
        'total_count': courses_count if courses_count else None,
        'filters': {
            'name': name,
            'course_unique_code': course_unique_code,
            'is_active': is_active,
            'client_status': client_status,
            'status': course_status,
            'course_type': course_type,
            'category': category,
            'language': language,
            'sub_stream': sub_stream,
            'lms_client_id': lms_client_id,
        }
    }
    return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_details(request, course_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    try:
        # try:
        if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF, AccountRole.DISTRICT_ADMIN,
                            AccountRole.DISTRICT_ADMIN_STAFF]:
            get_course = Course.objects.annotate(lms_client_name=F('lms_client__client')).get(id=int(course_id))
            content = {
                "course": {
                    'course_unique_code': get_course.course_unique_code,
                    'course_name': get_course.course_name,
                    'course_type': get_course.course_type,
                    'location': get_course.location,
                    'category': get_course.category,
                    'course_description': get_course.course_description,
                    'course_content': get_course.course_content,
                    'course_objective': get_course.course_objective,
                    'course_image_url': get_course.course_image_url,
                    'partner_name': get_course.partner_name,
                    'instructor': get_course.instructor,
                    'duration': get_course.duration,
                    'number_of_videos': get_course.number_of_videos,
                    'language': get_course.language,
                    'main_stream': get_course.main_stream,
                    'sub_stream': get_course.sub_stream,
                    # 'course_outcomes': get_course.course_outcomes,
                    'system_requirements': get_course.system_requirements,
                    'has_subtitles': get_course.has_subtitles,
                    'reference_id': get_course.reference_id,
                    'is_active': get_course.is_active,
                    'client_status': get_course.client_status,
                    'created': get_course.created,
                    'lms_client_name': get_course.lms_client.client if get_course.lms_client_id else None,

                },
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        elif account_role == AccountRole.STUDENT:
            get_course = Course.objects.annotate(lms_client_name=F('lms_client__client')).get(id=int(course_id))
            student_course = StudentCourse.objects.filter(student__profile_student__user_id=request.user.id, course_id=get_course.id).first()
            content = {
                "course": {
                    'course_unique_code': get_course.course_unique_code,
                    'course_name': get_course.course_name,
                    'course_type': get_course.course_type,
                    'location': get_course.location,
                    'category': get_course.category,
                    'course_description': get_course.course_description,
                    'course_content': get_course.course_content,
                    'course_objective': get_course.course_objective,
                    'course_image_url': get_course.course_image_url,
                    'partner_name': get_course.partner_name,
                    'instructor': get_course.instructor,
                    'duration': get_course.duration,
                    'number_of_videos': get_course.number_of_videos,
                    'language': get_course.language,
                    'main_stream': get_course.main_stream,
                    'sub_stream': get_course.sub_stream,
                    # 'course_outcomes': get_course.course_outcomes,
                    'system_requirements': get_course.system_requirements,
                    'has_subtitles': get_course.has_subtitles,
                    'reference_id': get_course.reference_id,
                    'is_active': get_course.is_active,
                    'client_status': get_course.client_status,
                    'created': get_course.created,
                    'is_subscribed': True if student_course else False,
                    "progress": {
                        'progress_percentage': student_course.progress_percentage,
                        'assessment_status': student_course.assessment_status,
                        'course_complete': student_course.course_complete,
                        'certificate_issued': student_course.certificate_issued,
                        'certificate_issued_at': student_course.certificate_issued_at,
                    } if student_course else None,
                    'lms_client_name': get_course.lms_client.client if get_course.lms_client_id else None,

                },
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')

        elif account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:

            course_history_record_type = request.GET.get('course_history_record_type', None)
            query_course_history = {}
            if course_history_record_type:
                try:
                    query_course_history['record_type'] = int(course_history_record_type)
                except:
                    pass

            print(course_history_record_type)
            get_course = Course.objects.select_related('lms_client').get(id=int(course_id))
            get_course_histories = CourseHistory.objects.annotate(
                lms_client_name=F('lms_client__client'),
                approved_user=F('approved_by__username')).values(
                'id',
                'record_type',
                'id',
                'course_unique_code',
                'course_name',
                'course_description',
                'course_content',
                'course_objective',
                'course_image_url',
                'partner_name',
                'category',
                'instructor',
                'duration',
                'number_of_videos',
                'language',
                'sub_stream',
                # 'course_outcomes',
                'system_requirements',
                'has_subtitles',
                'reference_id',
                'is_active',
                'client_status',
                'status',
                'is_active',
                'approved_user',
                'lms_client_name',
                'lms_client_id',
                'created',
                'updated',
                'approved_user',
                'created',
            ).filter(course_id=course_id, **query_course_history).order_by('-created')
            content = {
                "course": {
                    'id': get_course.id,
                    'course_unique_code': get_course.course_unique_code,
                    'course_name': get_course.course_name,
                    'course_type': get_course.course_type,
                    'location': get_course.location,
                    'category': get_course.category,
                    'course_description': get_course.course_description,
                    'course_content': get_course.course_content,
                    'course_objective': get_course.course_objective,
                    'course_image_url': get_course.course_image_url,
                    'partner_name': get_course.partner_name,
                    'instructor': get_course.instructor,
                    'duration': get_course.duration,
                    'number_of_videos': get_course.number_of_videos,
                    'language': get_course.language,
                    'main_stream': get_course.main_stream,
                    'sub_stream': get_course.sub_stream,
                    # 'course_outcomes': get_course.course_outcomes,
                    'system_requirements': get_course.system_requirements,
                    'has_subtitles': get_course.has_subtitles,
                    'reference_id': get_course.reference_id,
                    'is_active': get_course.is_active,
                    'client_status': get_course.client_status,
                    'created': get_course.created,
                    'lms_client_name': get_course.lms_client.client if get_course.lms_client_id else None,
                    'lms_client': {
                        'client': get_course.lms_client.client,
                        'contact_name': get_course.lms_client.contact_name,
                        'contact_phone': get_course.lms_client.contact_phone,
                        'contact_email': get_course.lms_client.contact_email,
                        'is_active': get_course.lms_client.is_active,
                    } if get_course.lms_client else None
                },
                'courses_history_list': list(get_course_histories),

                'filter_by': {
                    'status': get_class_list(CourseStatus),
                    'record_type': get_class_list(RecordType),
                }
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        else:
            content = {
                "message": "You dont have the permission",
            }
            return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

    except Course.DoesNotExist:
        content = {
            "message": "Please provide valid course ID",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_history_details(request, course_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    try:
        if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF, AccountRole.DISTRICT_ADMIN,
                            AccountRole.DISTRICT_ADMIN_STAFF, AccountRole.STUDENT]:
            get_course = Course.objects.annotate(lms_client_name=F('lms_client__client')).get(id=int(course_id),
                                                                                              is_active=True,
                                                                                              status=CourseStatus.APPROVED)
            content = {
                "course": {
                    'course_unique_code': get_course.course_unique_code,
                    'course_name': get_course.course_name,
                    'course_type': get_course.course_type,
                    'location': get_course.location,
                    'category': get_course.category,
                    'course_description': get_course.course_description,
                    'course_content': get_course.course_content,
                    'course_objective': get_course.course_objective,
                    'course_image_url': get_course.course_image_url,
                    'partner_name': get_course.partner_name,
                    'instructor': get_course.instructor,
                    'duration': get_course.duration,
                    'number_of_videos': get_course.number_of_videos,
                    'language': get_course.language,
                    'main_stream': get_course.main_stream,
                    'sub_stream': get_course.sub_stream,
                    # 'course_outcomes': get_course.course_outcomes,
                    'system_requirements': get_course.system_requirements,
                    'has_subtitles': get_course.has_subtitles,
                    'reference_id': get_course.reference_id,
                    'is_active': get_course.is_active,
                    'client_status': get_course.client_status,
                    'created': get_course.created,
                    'lms_client_name': get_course.lms_client.client if get_course.lms_client_id else None,

                },
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        elif account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:

            course_history_record_type = request.GET.get('course_history_record_type', None)
            course_history_status = request.GET.get('course_history_status', None)
            query_course_history = {}
            if course_history_record_type:
                try:
                    query_course_history['record_type'] = int(course_history_record_type)
                except:
                    pass

            if course_history_status:
                try:
                    query_course_history['status'] = int(course_history_status)
                except:
                    pass

            get_course = Course.objects.select_related('lms_client').get(id=int(course_id))
            get_course_histories = CourseHistory.objects.annotate(
                lms_client_name=F('lms_client__client'),
                approved_user=F('approved_by__username')).values(
                'id',
                'record_type',
                'id',
                'course_unique_code',
                'status',
                'course_name',
                'course_description',
                'course_content',
                'course_objective',
                'course_image_url',
                'partner_name',
                'category',
                'instructor',
                'duration',
                'number_of_videos',
                'language',
                'sub_stream',
                # 'course_outcomes',
                'system_requirements',
                'has_subtitles',
                'reference_id',
                'is_active',
                'client_status',
                'status',
                'is_active',
                'approved_user',
                'lms_client_name',
                'lms_client_id',
                'created',
                'updated',
                'approved_user',
                'created',
            ).filter(course_id=course_id, **query_course_history).order_by('-created')
            content = {
                "course": {
                    'id': get_course.id,
                    'course_unique_code': get_course.course_unique_code,
                    'status': get_course.status,
                    'course_name': get_course.course_name,
                    'course_type': get_course.course_type,
                    'location': get_course.location,
                    'category': get_course.category,
                    'course_description': get_course.course_description,
                    'course_content': get_course.course_content,
                    'course_objective': get_course.course_objective,
                    'course_image_url': get_course.course_image_url,
                    'partner_name': get_course.partner_name,
                    'instructor': get_course.instructor,
                    'duration': get_course.duration,
                    'number_of_videos': get_course.number_of_videos,
                    'language': get_course.language,
                    'main_stream': get_course.main_stream,
                    'sub_stream': get_course.sub_stream,
                    # 'course_outcomes': get_course.course_outcomes,
                    'system_requirements': get_course.system_requirements,
                    'has_subtitles': get_course.has_subtitles,
                    'reference_id': get_course.reference_id,
                    'is_active': get_course.is_active,
                    'client_status': get_course.client_status,
                    'created': get_course.created,
                    'lms_client_name': get_course.lms_client.client if get_course.lms_client_id else None,
                    'lms_client': {
                        'client': get_course.lms_client.client,
                        'contact_name': get_course.lms_client.contact_name,
                        'contact_phone': get_course.lms_client.contact_phone,
                        'contact_email': get_course.lms_client.contact_email,
                        'is_active': get_course.lms_client.is_active,
                    } if get_course.lms_client else None
                },
                'courses_history_list': list(get_course_histories),

                'filter_by': {
                    'status': get_class_list(CourseStatus),
                    'record_type': get_class_list(RecordType),
                }
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        else:
            content = {
                "message": "You dont have the permission",
            }
            return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

    except Course.DoesNotExist:

        content = {
            "message": "Please provide valid course ID",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_update(request, course_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    query = {}
    course_history_id = request.POST.get('course_history_id', None)
    name = request.POST.get('name', None)
    is_active = request.POST.get('is_active', None)
    record_status = request.POST.get('status', None)
    try:
        course_history_id = int(course_history_id)
        record_status = int(record_status)
    except Exception as e:
        print(e)
        content = {
            "message": "Please provide course_id/ course_history_id/ status",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    try:
        if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
            get_course_history = CourseHistory.objects.select_related('course',
                                                                      'course__lms_client').get(id=course_history_id,
                                                                                                course_id=course_id)
            if CourseStatus.APPROVED == record_status:
                course = get_course_history.course
                if course:
                    course.course_name = get_course_history.course_name if get_course_history.course_name else course.course_name
                    course.course_unique_code = get_course_history.course_unique_code if get_course_history.course_unique_code else course.course_unique_code
                    course.course_type = get_course_history.course_type if get_course_history.course_type else course.course_type
                    course.location = get_course_history.location if get_course_history.location else course.location
                    course.course_description = get_course_history.course_description if get_course_history.course_description else course.course_description
                    course.course_content = get_course_history.course_content if get_course_history.course_content else course.course_content
                    course.course_objective = get_course_history.course_objective if get_course_history.course_objective else course.course_objective
                    course.course_image_url = get_course_history.course_image_url if get_course_history.course_image_url else course.course_image_url
                    course.partner_name = get_course_history.partner_name if get_course_history.partner_name else course.partner_name
                    course.category = get_course_history.category if get_course_history.category else course.category
                    course.instructor = get_course_history.instructor if get_course_history.instructor else course.instructor
                    course.duration = get_course_history.duration if get_course_history.duration else course.duration
                    course.number_of_videos = get_course_history.number_of_videos if get_course_history.number_of_videos else course.number_of_videos
                    course.language = get_course_history.language if get_course_history.language else course.language
                    course.main_stream = get_course_history.main_stream if get_course_history.main_stream else course.main_stream
                    course.sub_stream = get_course_history.sub_stream if get_course_history.sub_stream else course.sub_stream
                    # course.course_outcomes = get_course_history.course_outcomes if get_course_history.course_outcomes else course.course_outcomes
                    course.system_requirements = get_course_history.system_requirements if get_course_history.system_requirements else course.system_requirements
                    course.has_subtitles = get_course_history.has_subtitles if get_course_history.has_subtitles else course.has_subtitles
                    course.reference_id = get_course_history.reference_id if get_course_history.reference_id else course.reference_id
                    course.is_active = get_course_history.is_active if get_course_history.is_active else course.is_active
                    course.status = 1
                    course.save()

                get_course_history.status = CourseStatus.APPROVED
                get_course_history.save()
                try:
                    if course.lms_client:
                        mail = send_mail_to_client(to_mail=course.lms_client.contact_email, course=course,
                                                   course_status=get_course_history.status)
                except:
                    pass
                content = {
                    'message': "Approved successfully"
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            elif CourseStatus.REJECTED == record_status:
                get_course_history.status = CourseStatus.REJECTED
                get_course_history.save()

                course = get_course_history.course
                course.status = 2
                course.save()
                try:
                    if course.lms_client:
                        mail = send_mail_to_client(
                            to_mail=course.lms_client.contact_email,
                            course=course,
                            course_status=get_course_history.status)
                except Exception as e:
                    pass
                content = {
                    'message': "Rejected successfully"
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')
            else:
                content = {
                    "message": "Please provide status",
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        else:
            content = {
                "message": "You dont have the permission",
            }
            return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

    except CourseHistory.DoesNotExist:

        content = {
            "message": "Please provide valid course ID / course history ID",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
