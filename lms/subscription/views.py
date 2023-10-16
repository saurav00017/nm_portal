from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.utils import timezone
from cerberus import Validator
import yaml
import jwt
from django.conf import settings
from django.shortcuts import render
from django.db.models.functions import Lower
from users.models import User, AccountRole, UserDetail
from django.db.models import F
from datarepo.views import get_class_list
# Create your views here.
import uuid

from django.conf import settings
from django.template.loader import get_template
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from nm_portal.config import Config
from skillofferings.models import SKillOfferingEnrollment, SKillOffering, SKillOfferingEnrollmentProgress
from .client_api import api_subscribe, api_course_watch_url
from kp.models import KnowledgePartner
from ..models import LMSClient, Course, CourseStatus, StudentCourse, RecordType, CourseHistory, StudentCourseSubscription
from simple.models import SimpleCourse


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


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_subscription(request):
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
                check_student_subscription = StudentCourse.objects.filter(
                    course_id=get_course.id,
                    student_id=get_profile.student_id).first()
                if check_student_subscription:
                    content = {
                        'message': "You have already subscribed for this course",
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                print("--> ",get_course.lms_client_id)

                is_mandatory = None
                try:
                    get_skill_offering = SKillOffering.objects.filter(lms_course_id=get_course.id).first()
                    if get_skill_offering:
                        is_mandatory = get_skill_offering.is_mandatory

                except:
                    get_skill_offering = None
                    try:
                        simple_course = SimpleCourse.objects.filter(lms_course_id=course_id).first()
                        if simple_course:
                            is_mandatory = 9
                    except:
                        pass
                new_subscription = StudentCourse(
                    student_id=get_profile.student_id,
                    course_id=get_course.id,
                    lms_client_id=get_course.lms_client_id,
                    is_mandatory=is_mandatory
                )
                lms_subscribe, error_message = api_subscribe(new_subscription)

                if lms_subscribe:
                    offering_type = None
                    if get_course.course_type == "ONLINE":
                        offering_type = 1
                    else:
                        offering_type = 0
                    get_knowledge_partner = KnowledgePartner.objects.get(lms_client_id=get_course.lms_client_id)
                    try:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                            student_id=get_profile.student_id,
                            college_id=get_profile.student.college_id if get_profile.student_id else None,
                            lms_course_id=get_course.id,
                            skill_offering_id=get_skill_offering.id if get_skill_offering else None,
                            # vendor=get_knowledge_partner.name if get_knowledge_partner else None,
                            knowledge_partner_id=get_knowledge_partner.id if get_knowledge_partner else None,

                        )
                    except SKillOfferingEnrollment.DoesNotExist:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                            student_id=get_profile.student_id,
                            college_id=get_profile.student.college_id if get_profile.student_id else None,
                            lms_course_id=get_course.id,
                            skill_offering_id=get_skill_offering.id if get_skill_offering else None,
                            offering_type=1,
                            offering_kind=1,
                            is_mandatory=get_skill_offering.is_mandatory if get_skill_offering else 0,
                            # vendor=get_knowledge_partner.name if get_knowledge_partner else None,
                            knowledge_partner_id=get_knowledge_partner.id if get_knowledge_partner else None,
                            status=4,  # Approved Directly by KP
                        )
                    content = {
                        'message': "Course subscribed successfully",
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                else:
                    content = {
                        'message': "Failed to get course detail from training provider. Please try again in few minutes. If issue still persist, contact your spoc. Thank you",
                        'kp_message': "KP - " + str(error_message),
                        'subscription_status': lms_subscribe
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            except Exception as e:
                content = {
                    'message': "Please provide course id",
                    "Exception": str(e)
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        content = {
            'message': "Please provide course id",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "You dont have a permission",
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_subscribed_watch_url(request):
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
                get_profile = UserDetail.objects.values('student_id', 'student__college__mandatory_release').get(user_id=request.user.id)
                skill_offering_data = None
                is_mandatory = None
                try:
                    get_skill_offering = SKillOffering.objects.filter(lms_course_id=course_id).order_by('-id').first()
                    if get_skill_offering:
                        is_mandatory = get_skill_offering.is_mandatory
                        # skill_offering_data = {
                        #     "get_skill_offering_id": get_skill_offering.id,
                        #     "is_mandatory": get_skill_offering.is_mandatory,
                        #     "mandatory_release": get_profile['student__college__mandatory_release'],
                        # }
                        if get_skill_offering.is_mandatory == 1 and not get_profile['student__college__mandatory_release']:
                            return Response({'message': 'Sorry, Mandatory course not released to you'}, status.HTTP_200_OK, content_type='application/json')

                except Exception as e:
                    get_skill_offering = None
                    # skill_offering_data = {
                    #     "error": str(e)
                    # }
                    try:
                        simple_course = SimpleCourse.objects.filter(lms_course_id=course_id).first()
                        if simple_course:
                            is_mandatory = 9
                    except:
                        pass

                try:
                    subscription = StudentCourse.objects.get(
                        student_id=get_profile['student_id'],
                        course_id=course_id,
                    )
                    if subscription.lms_client.client == "L & T Edu":
                        lms_subscribe, error_message = api_subscribe(subscription)
                except StudentCourse.MultipleObjectsReturned:

                    subscription = StudentCourse.objects.filter(
                        student_id=get_profile['student_id'],
                        course_id=course_id,
                    ).order_by('-created').first()
                    if subscription.lms_client.client == "L & T Edu":
                        lms_subscribe, error_message = api_subscribe(subscription)

                except StudentCourse.DoesNotExist:
                    """If Student Course does not Exist
                    
                    1. First check with 'course/access' api with student_unique_id & course_unique_code
                    2. if - we got the access_url from the 'course/access' api
                        1. Assume that student_unique_id & course_unique_code has been already subscribed
                        2. Create a new StudentCourse record
                        3. return the watch_url
                    
                    3. subscribe student to the course with student_unique_id & course_unique_code
                    4. if subscription status is True
                        1. request the api 'course/access'
                        2. return watch_url
                    5. else return the error message 
                    """
                    course = Course.objects.get(id=course_id)

                    subscription = StudentCourse(
                        student_id=get_profile['student_id'],
                        course_id=course_id,
                        lms_client_id=course.lms_client_id,
                        is_mandatory=is_mandatory
                    )

                    # access_status, access_url, error_message = api_course_watch_url(subscription)
                    # if access_status:
                    #     new_subscription = StudentCourse.objects.create(
                    #         student_id=get_profile['student_id'],
                    #         course_id=course_id,
                    #         status=StudentCourseSubscription.SUBSCRIBED_SUCCESS,
                    #         subscription_reference_id=subscription.subscription_reference_id,
                    #         subscription_on=timezone.now(),
                    #         lms_client_id=course.lms_client_id,
                    #         is_mandatory=is_mandatory
                    #     )
                    #     new_subscription.save()
                    #     content = {
                    #         'watch_url': access_url,
                    #     }
                    #     return Response(content, status.HTTP_200_OK, content_type='application/json')

                    lms_subscribe, error_message = api_subscribe(subscription)
                    if not lms_subscribe:
                        access_status, access_url, error_message = api_course_watch_url(subscription)
                        if access_status:
                            new_subscription = StudentCourse.objects.create(
                                student_id=get_profile['student_id'],
                                course_id=course_id,
                                status=StudentCourseSubscription.SUBSCRIBED_SUCCESS,
                                subscription_reference_id=subscription.subscription_reference_id,
                                subscription_on=timezone.now(),
                                lms_client_id=course.lms_client_id,
                                is_mandatory=is_mandatory
                            )
                            new_subscription.save()

                            content = {
                                'watch_url': access_url,
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')
                        content = {
                            'message': "Failed to get course detail from training provider. Please try again in few minutes. If issue still persist, contact your spoc. Thank you",
                            'kp_message': "KP - " + str(error_message),
                            'subscription_status': lms_subscribe,
                            # "skill_offering_data": skill_offering_data
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                access_status, access_url, error_message = api_course_watch_url(subscription)
                if access_status:
                    content = {
                        'watch_url': access_url,
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')

                else:
                    lms_subscribe, error_message = api_subscribe(subscription)
                    if lms_subscribe:
                        access_status, access_url, error_message = api_course_watch_url(subscription)
                        if access_status:
                            content = {
                                'watch_url': access_url,
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')

                    content = {
                        'message': "Failed to get course detail from training provider. Please try again in few minutes. If issue still persist, contact your spoc. Thank you",
                        'kp_message': "KP - " + str(error_message),
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            except Exception as e:
                print("lms_course_subscribed_watch_url", e)
                content = {
                    'message': "Please try again later",
                    "error": str(e)
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "Please try again later",
                "error": "Please provide course_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "You dont have a permission",
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def lms_course_subscribed_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if account_role == AccountRole.STUDENT:
        try:
            get_profile = UserDetail.objects.select_related('student').get(user_id=request.user.id)
            courses_list = StudentCourse.objects.select_related(
                'course',
                'lms_client',
            ).filter(student_id=get_profile.student_id).order_by(Lower('course__course_name'))

            final_courses_list = []
            for subscribe in courses_list:
                get_course = subscribe.course
                course = {
                    'course_id': get_course.id,
                    'progress': {
                        'progress_percentage': subscribe.progress_percentage,
                        'assessment_status': subscribe.assessment_status,
                        'course_complete': subscribe.course_complete,
                        'certificate_issued': subscribe.certificate_issued,
                        'certificate_issued_at': subscribe.certificate_issued_at,
                    },
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
                } if subscribe.course_id else None

                lms_client = subscribe.lms_client

                temp_subscribe = {
                    **dict(course),
                    'status': subscribe.status,
                    'progress_percentage': subscribe.progress_percentage,
                    'assessment_status': subscribe.assessment_status,
                    'course_complete': subscribe.course_complete,
                    'certificate_issued': subscribe.certificate_issued,
                    'subscription_on': subscribe.subscription_on,
                    'created': subscribe.created,
                    'lms_client': {
                        'client': lms_client.client,
                        'client_logo': lms_client.client_logo.url if lms_client.client_logo else None,

                    } if lms_client else None
                }
                final_courses_list.append(temp_subscribe)
            content = {
                'courses_list': final_courses_list,
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except Exception as e:
            print(e)
            content = {
                'message': "Please try again later",
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "You dont have a permission",
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
