from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail

from django.conf import settings
from skillofferings.models import SKillOfferingEnrollment, SKillOffering, SKillOfferingEnrollmentProgress
from college.models import College
from student.models import Student
from student.models import Student

from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q

@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def assessment_data_check(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    course_id = request.POST.get('course_id', None)
    course_code = request.POST.get('course_code', None)
    student_id = request.POST.get('student_id', None)
    skill_offering_id = request.POST.get('skill_offering_id', None)
    if account_role == AccountRole.NM_ADMIN:
        if not (course_id or course_code or skill_offering_id) or student_id is None:
            content = {
                'message': "Provide course_id or course_code or skill_offering_id / student_id",
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        try:
            student = Student.objects.get(invitation_id=student_id)
            if course_id:
                enrolled_progress_records = SKillOfferingEnrollmentProgress.objects.filter(
                    skill_offering_enrollment__student_id=student_id,
                    skill_offering_enrollment__skill_offering__lms_course_id=course_id,
                )
            elif course_code:

                enrolled_progress_records = SKillOfferingEnrollmentProgress.objects.filter(

                    Q(
                        Q(skill_offering_enrollment__skill_offering__lms_course__course_unique_code=course_code)|
                        Q(skill_offering_enrollment__skill_offering__course_code=course_code)
                    ),
                    skill_offering_enrollment__student_id=student.id,
                )
            elif skill_offering_id:
                enrolled_progress_records = SKillOfferingEnrollmentProgress.objects.filter(
                    skill_offering_enrollment__student_id=student.id,
                    skill_offering_enrollment__skill_offering_id=skill_offering_id,
                )
            else:
                content = {
                    'message': "Provide course_id/ course_code",
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            content = {
                'records_count': enrolled_progress_records.count(),
                'data': [{
                    'total_score': record.progress_percentage,
                    'assessment_status': record.assessment_status,
                    'certificate_issued': record.certificate_issued,
                    'course_complete': record.course_complete,
                    'assessment_data': record.assessment_data,
                }
                    for record in enrolled_progress_records
                ]
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')

        except Exception as e:

            content = {
                'message': "error",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')



    content = {
        'message': "You dont have a permission",
    }
    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

import csv

@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def assessment_data_csv_report(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    csv_file = request.POST.get('csv_file', None)
    skill_offering_id = request.POST.get('skill_offering_id', None)
    lms_course_id = request.POST.get('lms_course_id', None)
    lms_client_id = request.POST.get('lms_client_id', None)
    student_id = request.POST.get('student_id', None)
    download = request.POST.get('download', None)

    if account_role == AccountRole.NM_ADMIN:
        try:
            college_codes = []
            data = csv.reader(csv_file)
            for record in data:
                if record:
                    college_code = record[0]
                    if college_code:
                        college_codes.append(college_code)
            college_ids = College.objects.values_list('id', flat=True).filter(college_code__in=college_codes)

            student_ids = Student.objects.values_list('id', flat=True).filter(college_id__in=college_ids)
            skill_offering = SKillOffering.objects.get(id=skill_offering_id)
            enrollment_list = SKillOfferingEnrollment.objects.filter(
                skill_offering_id=skill_offering.id,
                student_id__in=student_ids
            )
            enrollment_ids = enrollment_list.values_list('id', flat=True)

            enrollment_progress_list = SKillOfferingEnrollmentProgress.objects.values('assessment_data').filter(
                skill_offering_enrollment_id__in=enrollment_ids
            )

            total_count = enrollment_progress_list.count()
            unique_count = enrollment_progress_list.distinct(
                'skill_offering_enrollment__skill_offering_id',
                'skill_offering_enrollment__student_id',
            ).count()
            counter = {}
            serial_level_counter = {}
            college_count = len(college_ids)

            for record in enrollment_progress_list:
                assessment_data = record['assessment_data']
                serial_ids = []
                if assessment_data and type(assessment_data) == dict:
                    serial = assessment_data['serial']
                    if serial not in serial_ids:
                        serial_ids.append(serial)

                elif assessment_data and type(assessment_data) == list:
                    for assessment in assessment_data:
                        serial = assessment['serial']
                        if serial not in serial_ids:
                            serial_ids.append(serial)
                else:
                    if 'not_yet_submitted' in counter:
                        counter['not_yet_submitted'] += 1
                    else:
                        counter['not_yet_submitted'] = 1

                for serial_id in serial_ids:

                    if serial_id in serial_level_counter:
                        serial_level_counter[serial_id] += 1
                    else:
                        serial_level_counter[serial_id] = 1

            serial_level_counter['not_yet_submitted'] = counter['not_yet_submitted']

            # for key, value in serial_level_counter.items():
            #     print(f"Assessment ({key}) - {value}")
            #
            serial_list = list(serial_level_counter.keys())
            if download == '1':
                response = HttpResponse(content_type='text/csv')
                filename = "mandatory_course_report_" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
                response['Content-Disposition'] = f'attachment; filename={filename}.csv'
                writer = csv.writer(response)
                headers = ['course', 'college_count'] + list(serial_level_counter.keys())


            content = {
                college_count: college_count,
                'total_enrollment_progress_count': total_count,
                'unique_enrollment_progress_count': unique_count,
                'duplicate_count': total_count - unique_count,
                'serial_list': serial_list,
                'assessments_submit_list': [
                    {
                        "assessment": key,
                        "count": value
                    } for key, value in serial_level_counter.items()
                ]
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except Exception as e:
            content = {
                'message': "Error",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    content = {
        'message': "You dont have a permission",
    }
    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
