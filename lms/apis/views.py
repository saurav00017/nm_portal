from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
import yaml
from users.models import User, UserDetail
from datarepo.models import PaymentStatus, StudentRegistrationStatus
from datarepo.views import get_class_list
from college.models import CollegeSubscription, CollegeStatus
from student.models import Student, StudentPaymentDetail
from django.conf import settings
from django.utils.timezone import datetime, timedelta
from datarepo.models import AccountRole
from ..models import LMSClient, Course, CourseStatus, CourseHistory, StudentCourse
from django.db.models import F
import os
from django.utils import timezone
import jwt
from skillofferings.models import SKillOfferingEnrollment, SKillOffering, SKillOfferingEnrollmentProgress
import json
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


@api_view(['POST'])
def api_login(request):
    try:
        json_data = json.loads(request.body)
        username = json_data.get('client_key', None)
        password = json_data.get('client_secret', None)
        request_schema = '''
            client_key:
                type: string
                empty: false
                required: true
                minlength: 5
            client_secret:
                type: string
                empty: false
                min: 6
                required: true
                minlength: 6
            '''
        v = Validator()
        post_data = json_data
        print(post_data)
        schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
        if v.validate(post_data, schema):

            # client_key = request.headers.get('CLIENT_KEY', None)
            # print(request.headers)
            # client_secret_key = request.headers.get('CLIENT_SECRET_KEY', None)
            # if client_key and client_secret_key:
            user = authenticate(username=username, password=password)
            if user:
                if user.account_role == AccountRole.LMS_API_USER:
                    check_client = True
                    # check_client = LMSClient.objects.filter(key=client_key, secret_key=client_secret_key, user_id=user.id).exists()
                    if check_client:
                        refresh_token = TokenObtainPairSerializer.get_token(user=user)
                        content = {
                            'token': str(refresh_token.access_token),
                            'refresh': str(refresh_token),
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                    else:
                        content = {
                            'message': "Please provide valid client key/ client secret in headers",
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            content = {
                'message': "Please provide valid client key/ client secret",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            # else:
            #
            #     content = {
            #         'message': "Please provide client key/ secret in headers",
            #     }
            #     return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "invalid request",
                'errors': v.errors
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def api_token_refresh(request):
    try:

        json_data = json.loads(request.body)
        refresh = json_data.get('refresh', None)
        request_schema = '''
            refresh:
                type: string
                empty: false
                required: true
            '''
        v = Validator()
        post_data = json_data
        schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
        if v.validate(post_data, schema):
            try:

                refresh = RefreshToken(refresh)
                content = {
                    'token': str(refresh.access_token),
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            except TokenError:
                content = {
                    'message': 'Token is invalid or expired',
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

        else:
            content = {
                'message': "invalid request",
                'errors': v.errors
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def publish_course(request):
    try:
        user = User.objects.get(id=request.user.id)
        if user.account_role == AccountRole.LMS_API_USER:
            json_data = json.loads(request.body)
            course_unique_code = json_data.get('course_unique_code', None)
            course_name = json_data.get('course_name', None)
            course_type = json_data.get('course_type', None)
            location = json_data.get('location', None)
            course_description = json_data.get('course_description', None)
            course_content = json_data.get('course_content', None)
            course_objective = json_data.get('course_objective', None)
            course_image_url = json_data.get('course_image_url', None)
            partner_name = json_data.get('partner_name', None)
            category = json_data.get('category', None)
            instructor = json_data.get('instructor', None)
            duration = json_data.get('duration', None)
            number_of_videos = json_data.get('number_of_videos', None)
            language = json_data.get('language', None)
            main_stream = json_data.get('main_stream', None)
            sub_stream = json_data.get('sub_stream', None)
            # course_outcomes = json_data.get('course_outcomes', None)
            system_requirements = json_data.get('system_requirements', None)
            has_subtitles = json_data.get('has_subtitles', None)
            reference_id = json_data.get('reference_id', None)
            request_schema = '''
                course_name:
                    type: string
                    empty: false
                    required: true
                course_type:
                    type: string
                    empty: false
                    required: true
                location:
                    type: string
                    empty: true
                    required: false
                course_unique_code:
                    type: string
                    empty: false
                    required: true
                course_description:
                    type: string
                    empty: true
                    required: false
                course_objective:
                    empty: true
                    required: false
                course_content:
                    empty: true
                    required: false
                course_image_url:
                    type: string
                    empty: true
                    required: false
                partner_name:
                    type: string
                    empty: true
                    required: false
                instructor:
                    type: string
                    empty: true
                    required: false
                category:
                    type: string
                    empty: true
                    required: false
                duration:
                    type: string
                    empty: true
                    required: false
                course_name:
                    type: string
                    empty: true
                    required: false
                has_subtitles:
                    type: string
                    empty: true
                    required: false
                language:
                    type: string
                    empty: true
                    required: false
                main_stream:
                    type: string
                    empty: true
                    required: false
                reference_id:
                    type: string
                    empty: true
                    required: false
                sub_stream:
                    type: string
                    empty: true
                    required: false
                system_requirements:
                    type: string
                    empty: true
                    required: false
                number_of_videos:
                    type: string
                    empty: true
                    required: false
                '''
            v = Validator()
            post_data = json_data
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    course_unique_code = str(course_unique_code).strip()
                    course_name = str(course_name).strip()
                    course_type = str(course_type).strip()
                    location = str(location).strip()
                    course_description = str(course_description).strip()
                    course_content = str(course_content).strip() if course_content else None
                    course_objective = str(course_objective).strip() if course_objective else None
                    course_image_url = str(course_image_url).strip()
                    partner_name = str(partner_name).strip()
                    category = str(category).strip()
                    instructor = str(instructor).strip()
                    duration = float(duration)
                    number_of_videos = int(number_of_videos)
                    language = str(language).strip()
                    main_stream = str(main_stream).strip()
                    sub_stream = str(sub_stream).strip()
                    # course_outcomes = str(course_outcomes).strip()
                    system_requirements = str(system_requirements).strip()
                    has_subtitles = True if has_subtitles == 'true' else False
                    reference_id = str(reference_id).strip()
                    try:
                        if course_content:
                            course_content = str(course_content).replace("'", '"')
                            course_content = json.loads(course_content)
                            if len(course_content) == 0 or type(course_content) != list:
                                course_content = None
                            else:
                                for course_content_record in course_content:
                                    if 'content' not in course_content_record:
                                        content = {
                                            'message': "Please provide valid json format course content",
                                            'course_content_error': course_content_record
                                        }
                                        return Response(content, status=status.HTTP_400_BAD_REQUEST,
                                                        content_type='application/json')

                        if course_objective:
                            course_objective = str(course_objective).replace("'", '"')
                            course_objective = json.loads(course_objective)
                            if len(course_objective) == 0 or type(course_objective) != list:
                                course_objective = None
                            else:
                                for course_objective_record in course_objective:
                                    if 'objective' not in course_objective_record:
                                        content = {
                                            'message': "Please provide valid json format course objective",
                                            'course_objective_error': course_objective_record
                                        }
                                        return Response(content, status=status.HTTP_400_BAD_REQUEST,
                                                        content_type='application/json')
                    except Exception as e:
                        print("Error", e)
                        content = {
                            'message': "Please add valid json format course content/ objective",
                        }
                        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                except Exception as e:
                    print("Error", e)
                    content = {
                        'message': "Please add valid data",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                get_lms_client = LMSClient.objects.get(user_id=request.user.id)
                if get_lms_client.is_active:
                    try:
                        get_course = Course.objects.get(course_unique_code=course_unique_code,
                                                        lms_client_id=get_lms_client.id)
                        # check_course_changes = Course.objects.filter(
                        #     course_unique_code=course_unique_code,
                        #     lms_client_id=get_lms_client.id
                        # ).exists()
                        # if check_course_changes:
                        #     content = {
                        #         'message': "No changes found",
                        #     }
                        #     return Response(content, status=status.HTTP_400_BAD_REQUEST,
                        #                     content_type='application/json')

                        new_course_history = CourseHistory.objects.create(
                            course_id=get_course.id,
                            course_unique_code=course_unique_code,
                            course_name=course_name,
                            location=location,
                            course_type=course_type,
                            course_description=course_description,
                            course_objective=course_objective,
                            course_content=course_content,
                            course_image_url=course_image_url,
                            partner_name=partner_name,
                            instructor=instructor,
                            category=category,
                            duration=duration,
                            number_of_videos=number_of_videos,
                            language=language,
                            main_stream=main_stream,
                            sub_stream=sub_stream,
                            # course_outcomes=course_outcomes,
                            system_requirements=system_requirements,
                            has_subtitles=has_subtitles,
                            reference_id=reference_id,
                            lms_client_id=get_lms_client.id
                        )
                        new_course_history.save()

                        content = {
                            'message': "Change request has initiated",
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                    except Course.DoesNotExist:
                        new_course = Course.objects.create(
                            course_unique_code=course_unique_code,
                            course_name=course_name,
                            location=location,
                            course_type=course_type,
                            course_description=course_description,
                            course_objective=course_objective,
                            course_content=course_content,
                            course_image_url=course_image_url,
                            partner_name=partner_name,
                            instructor=instructor,
                            category=category,
                            duration=duration,
                            number_of_videos=number_of_videos,
                            language=language,
                            main_stream=main_stream,
                            sub_stream=sub_stream,
                            # course_outcomes=course_outcomes,
                            system_requirements=system_requirements,
                            has_subtitles=has_subtitles,
                            reference_id=reference_id,
                            status=CourseStatus.NEW,
                            lms_client_id=get_lms_client.id
                        )
                        new_course_history = CourseHistory.objects.create(
                            course_id=new_course.id,
                            course_unique_code=course_unique_code,
                            course_name=course_name,
                            location=location,
                            course_type=course_type,
                            course_description=course_description,
                            course_objective=course_objective,
                            course_content=course_content,
                            course_image_url=course_image_url,
                            partner_name=partner_name,
                            instructor=instructor,
                            category=category,
                            duration=duration,
                            number_of_videos=number_of_videos,
                            language=language,
                            main_stream=main_stream,
                            sub_stream=sub_stream,
                            # course_outcomes=course_outcomes,
                            system_requirements=system_requirements,
                            has_subtitles=has_subtitles,
                            reference_id=reference_id,
                            lms_client_id=get_lms_client.id
                        )
                        new_course_history.save()
                        content = {
                            'message': "Course has been sent for approval , you will get email as confirmation",
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                else:
                    content = {
                        'message': "Account is deactivated. Please contact admin",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "You dont have the permission",
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    except User.DoesNotExist:
        content = {
            'message': "You dont have the permission",
        }
        return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_courses(request):
    try:
        course_name = request.GET.get('course_name', None)
        course_type = request.GET.get('course_type', None)
        course_unique_code = request.GET.get('course_unique_code', None)
        client_status = request.GET.get('status', None)
        page = request.GET.get('page', 0)
        limit = request.GET.get('limit', 20)
        user = User.objects.get(id=request.user.id)
        if user.account_role == AccountRole.LMS_API_USER:
            try:
                page = int(page)
                limit = int(limit)
            except:
                page = 0
                limit = 20
            query = {}
            if course_name:
                query['course_name__istartswith'] = course_name
            if course_unique_code:
                query['course_unique_code__istartswith'] = course_unique_code
            if client_status in ['0', '1', 1, 0]:
                query['course_status'] = int(client_status)

            get_lms_client = LMSClient.objects.get(user_id=request.user.id)
            print(get_lms_client)
            if get_lms_client.is_active:
                try:
                    courses_count = Course.objects.filter(**query,
                                                          lms_client_id=get_lms_client.id).count()
                    get_courses = Course.objects.values(
                        'course_unique_code',
                        'course_name',
                        'course_type',
                        'location',
                        'location',
                        'course_description',
                        'course_content',
                        'course_objective',
                        'course_image_url',
                        'partner_name',
                        'instructor',
                        'category',
                        'duration',
                        'number_of_videos',
                        'language',
                        'main_stream',
                        'sub_stream',
                        # 'course_outcomes',
                        'system_requirements',
                        'has_subtitles',
                        'reference_id',
                        'client_status',
                    ).filter(**query, lms_client_id=get_lms_client.id)[(page * limit): ((page * limit) + limit)]

                    content = {
                        'courses_list': list(get_courses),
                        'page': page,
                        'limit': limit,
                        'total_count': courses_count if courses_count else 0
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                except Exception as e:
                    print("Error", e)
                    content = {
                        'message': "Something went wrong! Please try again later",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "Account is deactivated. Please contact admin",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "You dont have the permission",
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')

    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    except User.DoesNotExist:
        content = {
            'message': "You dont have the permission",
        }
        return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def student_tracking(request):
    try:
        json_data = json.loads(request.body)
        student_id = json_data.get('user_unique_id', None)
        course_unique_code = json_data.get('course_unique_code', None)
        progress_percentage = json_data.get('total_score', None)
        certificate_issued = json_data.get('certificate_issued', None)
        certificate_issued_at = json_data.get('certificate_issued_at', None)
        assessment_status = json_data.get('assessment_status', None)
        course_complete = json_data.get('course_complete', None)
        assessment_data = json_data.get('assessment_data', None)
        missing_fields = []
        invalid_fields = []
        if assessment_data:
            score_error = None
            if 'score' not in assessment_data:
                missing_fields.append('score')
            else:
                # score_error = assessment_data['score']
                try:
                    if assessment_data['score'] in ["0", 0]:
                        score = 0
                    else:
                        score = float(assessment_data['score'])
                except Exception as e:
                    score = None
                if not score and score not in ["0", 0]:
                    invalid_fields.append('score' )
            if 'correct_answers' not in assessment_data:
                missing_fields.append('correct_answers')
            else:
                try:
                    if assessment_data['correct_answers'] in ["0", 0]:
                        correct_answers = 0
                    else:
                        correct_answers = int(assessment_data['correct_answers'])
                except:
                    correct_answers = None
                if not correct_answers and correct_answers not in ["0", 0]:
                    invalid_fields.append('correct_answers')
            if 'total_questions' not in assessment_data:
                missing_fields.append('total_questions')
            else:
                try:
                    if assessment_data['total_questions'] == "0":
                        total_questions = 0
                    else:
                        total_questions = int(assessment_data['total_questions'])
                except:
                    total_questions = None
                if not total_questions:
                    invalid_fields.append('total_questions')
            if 'serial' not in assessment_data:
                missing_fields.append('serial')
            else:
                try:
                    serial = int(assessment_data['serial'])
                except:
                    serial = None
                if not serial:
                    invalid_fields.append('serial')

            if 'attempt' not in assessment_data:
                missing_fields.append('attempt')
            else:
                try:
                    attempt = int(assessment_data['attempt'])
                except:
                    attempt = None
                if not attempt:
                    invalid_fields.append('attempt')

            if 'created' not in assessment_data:
                missing_fields.append('created')
            if 'updated' not in assessment_data:
                missing_fields.append('updated')

            if missing_fields or invalid_fields:
                content = {
                    'message': 'Please provide assessment_data',
                    'missing_fields': missing_fields,
                    'invalid_fields': invalid_fields,
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            assessment_data['submitted_on'] = timezone.now().strftime("%Y-%m-%d %H:%M%S")
        if certificate_issued:
            certificate_issued = True if str(certificate_issued).lower().strip() == "true" else False
        if assessment_status:
            assessment_status = True if str(assessment_status).lower().strip() == "true" else False
        if course_complete:
            course_complete = True if str(course_complete).lower().strip() == "true" else False
        try:
            student_id = str(student_id).strip()
            course_unique_code = str(course_unique_code).strip()
            progress_percentage = float(progress_percentage)
        except Exception as e:
            print("Error", e)
            content = {
                'message': 'Please provide user_unqiue_id/ course_unique_code/ '
                           'total_score/ certificate_issued/ assessment_status/ course_complete'
            }
            return Response(content, status=status.HTTP_200_OK, content_type='application/json')
        user = User.objects.values('account_role').get(id=request.user.id)
        if user['account_role'] == AccountRole.LMS_API_USER:
            get_lms_client = LMSClient.objects.get(user_id=request.user.id)
            print('course_unique_code', course_unique_code)
            print('student_id', student_id)
            if get_lms_client.is_active:
                try:
                    get_course = Course.objects.get(course_unique_code=course_unique_code, lms_client_id=get_lms_client.id)
                    get_student = Student.objects.get(invitation_id=student_id)
                    try:
                        get_student_course = StudentCourse.objects.get(
                            student_id=get_student.id,
                            course_id=get_course.id,
                        )

                    except StudentCourse.DoesNotExist:
                        if not get_lms_client.id==21:
                            get_student_course = StudentCourse.objects.create(
                                student_id=get_student.id,
                                course_id=get_course.id,
                                status=1,
                                subscription_on=timezone.now(),
                                lms_client_id=get_lms_client.id,
                                is_mandatory=1
                            )

                        else:
                            content = {
                                'message': "Please provide valid user_unique_id/ course_unique_code",
                            }
                            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                    except StudentCourse.MultipleObjectsReturned:

                        get_student_courses = StudentCourse.objects.filter(
                            student_id=get_student.id,
                            course_id=get_course.id,

                        )
                        get_student_course = get_student_courses.first()
                        delete_remaining = get_student_courses.exclude(id=get_student_course.id)
                        for record in delete_remaining:
                            record.delete()

                    try:
                        get_skill_offering = SKillOffering.objects.filter(lms_course_id=get_student_course.course_id).first()
                        if get_skill_offering:
                            get_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                                student_id=get_student_course.student_id,
                                skill_offering_id=get_skill_offering.id if get_skill_offering else None,
                            )
                            try:
                                skill_offering_enrollment_progress = SKillOfferingEnrollmentProgress.objects.get(
                                    skill_offering_enrollment_id=get_skill_offering_enrollment.id
                                )
                                if progress_percentage is not None:
                                    skill_offering_enrollment_progress.progress_percentage = progress_percentage
                                if assessment_status is not None:
                                    skill_offering_enrollment_progress.assessment_status = assessment_status
                                if course_complete is not None:
                                    skill_offering_enrollment_progress.course_complete = course_complete
                                if certificate_issued is not None:
                                    skill_offering_enrollment_progress.certificate_issued = certificate_issued
                                if certificate_issued_at is not None:
                                    skill_offering_enrollment_progress.certificate_issued_at = certificate_issued_at
                                skill_offering_enrollment_progress.save()
                                if assessment_data is not None:
                                    if skill_offering_enrollment_progress.assessment_data is None or skill_offering_enrollment_progress.assessment_data == "":
                                        skill_offering_enrollment_progress.assessment_data = [assessment_data]
                                    elif skill_offering_enrollment_progress.assessment_data is not None:
                                        if type(skill_offering_enrollment_progress.assessment_data) == list:
                                            already_exists = False
                                            for record in skill_offering_enrollment_progress.assessment_data:
                                                if record['score'] == assessment_data['score'] and \
                                                        record['serial'] == assessment_data['serial'] and \
                                                        record['attempt'] == assessment_data['attempt']:
                                                    content = {
                                                        'message': 'Assessment record with score/ serial/ attempt already exists. Total score updated successfully'
                                                    }
                                                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                                            skill_offering_enrollment_progress.assessment_data.append(assessment_data)
                                        else:
                                            record = skill_offering_enrollment_progress.assessment_data
                                            if record['score'] == assessment_data['score'] and \
                                                    record['serial'] == assessment_data['serial'] and \
                                                    record['attempt'] == assessment_data['attempt']:
                                                skill_offering_enrollment_progress.assessment_data = [skill_offering_enrollment_progress.assessment_data]
                                                skill_offering_enrollment_progress.save()
                                                content = {
                                                    'message': 'Assessment record with score/ serial/ attempt already exists'
                                                }
                                                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                                            skill_offering_enrollment_progress.assessment_data = [skill_offering_enrollment_progress.assessment_data, assessment_data]
                                skill_offering_enrollment_progress.save()
                            except SKillOfferingEnrollmentProgress.MultipleObjectsReturned:
                                skill_offering_enrollment_progress = SKillOfferingEnrollmentProgress.objects.filter(
                                    skill_offering_enrollment_id=get_skill_offering_enrollment.id
                                ).order_by('-created').first()
                                if progress_percentage is not None:
                                    skill_offering_enrollment_progress.progress_percentage = progress_percentage
                                if assessment_status is not None:
                                    skill_offering_enrollment_progress.assessment_status = assessment_status
                                if course_complete is not None:
                                    skill_offering_enrollment_progress.course_complete = course_complete
                                if certificate_issued is not None:
                                    skill_offering_enrollment_progress.certificate_issued = certificate_issued
                                if certificate_issued_at is not None:
                                    skill_offering_enrollment_progress.certificate_issued_at = certificate_issued_at
                                skill_offering_enrollment_progress.save()
                                if assessment_data is not None:
                                    if skill_offering_enrollment_progress.assessment_data is None or skill_offering_enrollment_progress.assessment_data == "":
                                        skill_offering_enrollment_progress.assessment_data = [assessment_data]
                                    elif skill_offering_enrollment_progress.assessment_data is not None:
                                        if type(skill_offering_enrollment_progress.assessment_data) == list:
                                            already_exists = False
                                            for record in skill_offering_enrollment_progress.assessment_data:
                                                if record['score'] == assessment_data['score'] and \
                                                        record['serial'] == assessment_data['serial'] and \
                                                        record['attempt'] == assessment_data['attempt']:
                                                    content = {
                                                        'message': 'Assessment record with score/ serial/ attempt already exists. Total score updated successfully'
                                                    }
                                                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                                            skill_offering_enrollment_progress.assessment_data.append(assessment_data)
                                        else:
                                            record = skill_offering_enrollment_progress.assessment_data
                                            if record['score'] == assessment_data['score'] and \
                                                    record['serial'] == assessment_data['serial'] and \
                                                    record['attempt'] == assessment_data['attempt']:
                                                skill_offering_enrollment_progress.assessment_data = [skill_offering_enrollment_progress.assessment_data]
                                                skill_offering_enrollment_progress.save()
                                                content = {
                                                    'message': 'Assessment record with score/ serial/ attempt already exists'
                                                }
                                                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
                                            skill_offering_enrollment_progress.assessment_data = [skill_offering_enrollment_progress.assessment_data, assessment_data]
                                skill_offering_enrollment_progress.save()
                            except SKillOfferingEnrollmentProgress.DoesNotExist:
                                skill_offering_enrollment_progress = SKillOfferingEnrollmentProgress.objects.create(
                                    skill_offering_enrollment_id=get_skill_offering_enrollment.id,
                                    knowledge_partner_id=get_skill_offering.knowledge_partner_id,
                                    progress_percentage=progress_percentage,
                                    assessment_status=assessment_status,
                                    certificate_issued=assessment_status,
                                    certificate_issued_at=certificate_issued_at,
                                    assessment_data=[assessment_data]
                                )
                    except:
                        get_skill_offering = None
                    if progress_percentage is not None:
                        get_student_course.progress_percentage = progress_percentage
                    if assessment_status is not None:
                        get_student_course.assessment_status = assessment_status
                    if course_complete is not None:
                        get_student_course.course_complete = course_complete
                    if certificate_issued is not None:
                        get_student_course.certificate_issued = certificate_issued
                    if certificate_issued_at is not None:
                        get_student_course.certificate_issued_at = certificate_issued_at
                    # if assessment_data is not None:
                        # if get_student_course.assessment_data is None or get_student_course.assessment_data == "":
                        #     get_student_course.assessment_data = [assessment_data]
                        # elif get_student_course.assessment_data is not None:
                        #     if type(get_student_course.assessment_data) == list:
                        #         get_student_course.assessment_data.append(assessment_data)
                        #     else:
                        #         get_student_course.assessment_data = [get_student_course.assessment_data, assessment_data]
                    get_student_course.save()
                    content = {
                        'message': 'user course details updated successfully',
                        "total_score": progress_percentage,
                        'id': get_student_course.id,
                        'skill_offering': get_skill_offering.id if get_skill_offering else None
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                except Student.DoesNotExist:
                    content = {
                        'message': "Student ID not found",
                        'student_id': student_id
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

                except Exception as e:
                    print("Error", e)
                    content = {
                        'message': "Something went wrong! Please try again later",
                        "error": str(e)
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "Account is deactivated. Please contact admin",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "You dont have the permission",
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')

    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    except User.DoesNotExist:
        content = {
            'message': "You dont have the permission",
        }
        return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def student_check(request):
    try:
        json_data = json.loads(request.body)
        student_id = json_data.get('user_unique_id', None)
        course_unique_code = json_data.get('course_unique_code', None)
        try:
            student_id = str(student_id).strip()
            course_unique_code = str(course_unique_code).strip()
        except Exception as e:
            print("Error", e)
            content = {
                'message': 'Please provide user_unqiue_id/ course_unique_code'
            }
            return Response(content, status=status.HTTP_200_OK, content_type='application/json')
        user = User.objects.values('account_role').get(id=request.user.id)
        if user['account_role'] == AccountRole.LMS_API_USER:
            get_lms_client = LMSClient.objects.get(user_id=request.user.id)
            if get_lms_client.is_active:
                try:
                    get_course = Course.objects.get(course_unique_code=course_unique_code, lms_client_id=get_lms_client.id)
                    get_student = Student.objects.get(invitation_id=student_id)
                    try:
                        get_student_course = StudentCourse.objects.get(student_id=get_student.id, course_id=get_course.id)
                    except StudentCourse.DoesNotExist:
                        content = {
                            'status': False
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                    except StudentCourse.MultipleObjectsReturned:
                        get_student_courses = StudentCourse.objects.filter(
                            student_id=get_student.id,
                            course_id=get_course.id,
                        )
                        get_student_course = get_student_courses.first()
                        delete_remaining = get_student_courses.exclude(id=get_student_course.id)
                        for record in delete_remaining:
                            record.delete()
                    content = {
                        'status': True
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')

                except Exception as e:
                    content = {
                        'status': False
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            else:
                content = {
                    'message': "Account is deactivated. Please contact admin",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "You dont have the permission",
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')

    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    except User.DoesNotExist:
        content = {
            'message': "You dont have the permission",
        }
        return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
