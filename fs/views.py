from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment, \
    SKillOfferingEnrollmentProgress
from django.db.models import Count
import csv
from io import StringIO
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail
from django.conf import settings
from student.models import Student
from kp.models import KnowledgePartner
from fs.models import FSCourse, FSEnrollment, FSEnrollmentProgress


@api_view(['GET'])
def fs_courses(request):
    kp_id = request.GET.get('kp_id', None)
    if kp_id is None:
        return Response(status=status.HTTP_200_OK, content_type='application/json', data={
            'status': False, 'message': 'kp_id is required'
        })
    try:
        kp_details = KnowledgePartner.objects.get(id=kp_id)
        return Response(status=status.HTTP_200_OK, content_type='application/json', data={
            'kp_details': {
                'id': kp_details.id,
                'name': kp_details.name,
                'description': kp_details.description,
                'website': kp_details.website,
                'logo': str('https://api.naanmudhalvan.tn.gov.in') + str(
                    kp_details.logo.url if kp_details.logo else None),
            },
            'fs_courses': [{
                'fs_course_id': x.id,
                'name': x.name,
                'description': x.description,
                'details': x.details,
            } for x in FSCourse.objects.filter(knowledge_partner_id=kp_id, status=3)]
        })
    except KnowledgePartner.DoesNotExist:
        return Response(status=status.HTTP_200_OK, content_type='application/json', data={
            'status': False, 'message': 'kp_id is invalid'
        })


@api_view(['POST', 'GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def enrollment(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if request.method == 'POST':
        if account_role == AccountRole.STUDENT:
            student_info = UserDetail.objects.get(user_id=request.user.id)
            if student_info.student.is_pass_out is False:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'You are not eligible to enroll in FS'
                })
            elif student_info.student.is_pass_out is True:
                fs_id = request.POST.get('fs_id', None)
                if fs_id is None:
                    return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                        'status': False, 'message': 'fs_id is required'
                    })
                try:
                    fs_details = FSCourse.objects.get(id=fs_id)
                    try:
                        fs_enrolment_check = FSEnrollment.objects.get(
                            fs_course_id=fs_id,
                            student_id=student_info.student_id
                        )
                        return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                            'status': False, 'message': 'You have already enrolled in this FS'
                        })
                    except FSEnrollment.DoesNotExist:
                        new_fs_enrollment = FSEnrollment.objects.create(
                            fs_course_id=fs_id,
                            student_id=student_info.student_id,
                            college_id=student_info.college_id,
                            status=0,
                            enrollment_type=fs_details.enrollment_type,
                            knowledge_partner_id=fs_details.knowledge_partner_id
                        )
                        new_fs_enrollment.save()
                        new_fs_enrollment_progress = FSEnrollmentProgress.objects.create(
                            fs_course_id=fs_id,
                            knowledge_partner_id=fs_details.knowledge_partner_id,
                        )
                        new_fs_enrollment_progress.save()
                        return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                            'status': True, 'message': 'You have successfully enrolled in this FS'
                        })
                except FSCourse.DoesNotExist:
                    return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                        'status': False, 'message': 'fs_id is invalid'
                    })
        elif account_role == AccountRole.KNOWLEDGE_PARTNER:
            kp_info = KnowledgePartner.objects.filter(user_id=request.user.id).first()
            if kp_info.is_fs is False:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'You are not eligible for FS program'
                })
            enrollment_id = request.POST.get('enrollment_id', None)
            enrollment_status = request.POST.get('enrollment_status', None)
            if enrollment_id is None:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'enrollment_id is required'
                })
            try:
                fs_enrolment = FSEnrollment.objects.get(
                    id=enrollment_id,
                    knowledge_partner_id=kp_info.id,
                )
                fs_enrolment.status = enrollment_status if enrollment_status is not None else fs_enrolment.status
                fs_enrolment.save()
                fs_enrolment_progress = FSEnrollmentProgress.objects.filter(
                    fs_course_id=fs_enrolment.fs_course_id,
                ).order_by('-id').first()
                progress_percentage = request.POST.get('progress_percentage', None)
                assessment_status = request.POST.get('assessment_status', None)
                course_complete = request.POST.get('course_complete', None)
                certificate_issued = request.POST.get('certificate_issued', None)
                fs_enrolment_progress.progress_percentage = progress_percentage if progress_percentage is not None else fs_enrolment_progress.progress_percentage
                fs_enrolment_progress.assessment_status = assessment_status if assessment_status is None else True if assessment_status == 'true' else False if assessment_status == 'false' else fs_enrolment_progress.assessment_status
                fs_enrolment_progress.course_complete = course_complete if course_complete is None else True if course_complete == 'true' else False if course_complete == 'false' else fs_enrolment_progress.course_complete
                fs_enrolment_progress.certificate_issued = certificate_issued if certificate_issued is None else True if certificate_issued == 'true' else False if certificate_issued == 'false' else fs_enrolment_progress.certificate_issued
                fs_enrolment_progress.save()
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': True, 'message': 'progress updated', 'data': {
                        'enrollment_id': fs_enrolment.id,
                        'enrollment_status': fs_enrolment.status,
                        'enrollment_comment': fs_enrolment.comment,
                        'student_id': fs_enrolment.student_id,
                        'student_name': fs_enrolment.student.first_name + ' ' + fs_enrolment.student.last_name,
                        'fs_course_details': {
                            'fs_course_id': fs_enrolment.fs_course_id,
                            'fs_course_name': fs_enrolment.fs_course.name,
                            'fs_course_description': fs_enrolment.fs_course.description,
                        },
                        'progress': {
                            'progress_percentage': fs_enrolment_progress.progress_percentage,
                            'assessment_status': fs_enrolment_progress.assessment_status,
                            'course_complete': fs_enrolment_progress.course_complete,
                            'certificate_issued': fs_enrolment_progress.certificate_issued,
                        }}
                })
            except FSEnrollment.DoesNotExist:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'enrollment not found'
                })


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def enrollments(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if request.method == 'GET':
        if account_role == AccountRole.STUDENT:
            student_info = UserDetail.objects.get(user_id=request.user.id)
            student_info = student_info.student
            if student_info.is_pass_out is False:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'You are not eligible to enroll in FS'
                })
            elif student_info.is_pass_out is True:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': True, 'data': [{
                        'enrollment_id': x.id,
                        'enrollment_status': x.status,
                        'enrollment_comment': x.comment,
                        'student_id': x.student_id,
                        'student_name': x.student.first_name + ' ' + x.student.last_name,
                        'fs_course_details': {
                            'fs_course_id': x.fs_course_id,
                            'fs_course_name': x.fs_course.name,
                            'fs_course_description': x.fs_course.description,
                        },
                    } for x in FSEnrollment.objects.filter(student_id=student_info.id)]
                })
        if account_role == AccountRole.KNOWLEDGE_PARTNER:
            kp_info = KnowledgePartner.objects.filter(user_id=request.user.id).first()
            if kp_info.is_fs is False:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'You are not eligible for FS program'
                })
            return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                'status': True, 'data': [{
                    'enrollment_id': x.id,
                    'enrollment_status': x.status,
                    'enrollment_comment': x.comment,
                    'student_id': x.student_id,
                    'student_name': x.student.first_name + ' ' + x.student.last_name,
                    'fs_course_details': {
                        'fs_course_id': x.fs_course_id,
                        'fs_course_name': x.fs_course.name,
                        'fs_course_description': x.fs_course.description,
                    },
                } for x in FSEnrollment.objects.filter(knowledge_partner_id=kp_info.id)]
            })


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def progress(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if request.method == 'GET':
        if account_role == AccountRole.STUDENT:
            student_info = UserDetail.objects.get(user_id=request.user.id)
            student_info = student_info.student
            if student_info.is_pass_out is False:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'You are not eligible to enroll in FS'
                })
            elif student_info.is_pass_out is True:
                enrollment_id = request.GET.get('enrollment_id', None)
                try:
                    fs_enrolment_check = FSEnrollment.objects.get(
                        id=enrollment_id,
                        student_id=student_info.id
                    )
                    fs_enrolment_progress_check = FSEnrollmentProgress.objects.get(
                        fs_course_id=fs_enrolment_check.fs_course_id
                    )
                    return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                        'status': True, 'data': {
                            'progress_percentage': fs_enrolment_progress_check.progress_percentage,
                            'assessment_status': fs_enrolment_progress_check.assessment_status,
                            'course_complete': fs_enrolment_progress_check.course_complete,
                            'certificate_issued': fs_enrolment_progress_check.certificate_issued,
                        }
                    })
                except FSEnrollment.DoesNotExist:
                    return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                        'status': False, 'message': 'enrollment not found'
                    })
        if account_role == AccountRole.KNOWLEDGE_PARTNER:
            kp_info = KnowledgePartner.objects.filter(user_id=request.user.id).first()
            if kp_info.is_fs is False:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'You are not eligible for FS program'
                })
            enrollment_id = request.GET.get('enrollment_id', None)
            try:
                fs_enrolment_check = FSEnrollment.objects.get(
                    id=enrollment_id,
                    knowledge_partner_id=kp_info.id
                )
                fs_enrolment_progress_check = FSEnrollmentProgress.objects.get(
                    fs_course_id=fs_enrolment_check.fs_course_id
                )
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': True, 'data': {
                        'progress_percentage': fs_enrolment_progress_check.progress_percentage,
                        'assessment_status': fs_enrolment_progress_check.assessment_status,
                        'course_complete': fs_enrolment_progress_check.course_complete,
                        'certificate_issued': fs_enrolment_progress_check.certificate_issued,
                    }
                })
            except FSEnrollment.DoesNotExist:
                return Response(status=status.HTTP_200_OK, content_type='application/json', data={
                    'status': False, 'message': 'enrollment not found'
                })
