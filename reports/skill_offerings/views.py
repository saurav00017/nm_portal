from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOffering, SKillOfferingEnrollmentProgress
import csv
from django.http import HttpResponse
from django.utils import timezone
from student.models import Student
from college.models import College
from lms.models import StudentCourse
from django.conf import settings
import jwt
from users.models import User, AccountRole, UserDetail
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.db.models import Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTTokenUserAuthentication])
def skill_offerings_overview_report(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    is_mandatory = request.GET.get('is_mandatory', None)
    view_all = request.GET.get('view_all', None)
    knowledge_partner_id = request.GET.get('knowledge_partner_id', None)
    sem = request.GET.get('sem', None)

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    skill_offering_query = {}
    if is_mandatory:
        skill_offering_query['is_mandatory'] = is_mandatory
    if knowledge_partner_id:
        skill_offering_query['knowledge_partner_id'] = knowledge_partner_id
    if sem:
        skill_offering_query['sem'] = sem

    if account_role == AccountRole.NM_ADMIN:
        skill_offerings_list = SKillOffering.objects.filter(**skill_offering_query)
        total_count = skill_offerings_list.count()
        if view_all == '1':
            limit = total_count

        final_skill_offerings = []
        for skill_offering in skill_offerings_list[(page * limit): ((page * limit) + limit)]:
            enrollment_count = SKillOfferingEnrollment.objects.filter(skill_offering_id=skill_offering.id).exclude(student_id=None).distinct(
                'skill_offering_id',
                'student_id',
            ).count()
            subscribed_count = StudentCourse.objects.filter(course_id=skill_offering.lms_course_id).exclude(student_id=None).distinct(
                'course_id',
                'student_id',
            ).count()
            temp_skill_offering = {
                'skill_offering_id': skill_offering.id,
                "course_name": skill_offering.course_name,
                'enrollment_count': enrollment_count,
                'subscribed_count': subscribed_count,
                'is_mandatory': skill_offering.is_mandatory,
                'knowledge_partner_id': skill_offering.knowledge_partner_id,
                'knowledge_partner_name': skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else None,
            }
            final_skill_offerings.append(temp_skill_offering)
        content = {
            "reports": final_skill_offerings,
            "filters": {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'view_all': view_all,
                'is_mandatory': is_mandatory,
                'knowledge_partner_id': knowledge_partner_id,
                'sem': sem,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    elif account_role == AccountRole.COLLEGE_ADMIN:
        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            skill_offering_ids = SKillOfferingEnrollment.objects.select_realted('student').values_list('skill_offering_id', flat=True).filter(
                student__college_id=user_details.college_id
            )
            skill_offerings_list = SKillOffering.objects.filter(
                skill_offering_id__in=skill_offering_ids,
                **skill_offering_query)
            total_count = skill_offerings_list.count()
            if view_all == '1':
                limit = total_count

            final_skill_offerings = []
            for skill_offering in skill_offerings_list[(page * limit): ((page * limit) + limit)]:
                enrollment_count = SKillOfferingEnrollment.objects.select_related('student').filter(
                    student__college_id=user_details.college_id,
                    skill_offering_id=skill_offering.id).distinct(
                    'skill_offering_id',
                    'student_id',
                ).count()
                subscribed_count = StudentCourse.objects.select_related('student').filter(
                    student__college_id=user_details.college_id,
                    course_id=skill_offering.lms_course_id).exclude(student_id=None).distinct(
                    'course_id',
                    'student_id',
                ).count()
                temp_skill_offering = {
                    'skill_offering_id': skill_offering.id,
                    "course_name": skill_offering.course_name,
                    'enrollment_count': enrollment_count,
                    'subscribed_count': subscribed_count,
                    'is_mandatory': skill_offering.is_mandatory,
                    'knowledge_partner_id': skill_offering.knowledge_partner_id,
                    'knowledge_partner_name': skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else None,
                }
                final_skill_offerings.append(temp_skill_offering)
            content = {
                "reports": final_skill_offerings,
                "filters": {
                    'page': page,
                    'limit': limit,
                    'total_count': total_count,
                    'view_all': view_all,
                    'is_mandatory': is_mandatory,
                    'knowledge_partner_id': knowledge_partner_id,
                    'sem': sem,
                }
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except Exception as e:
            content = {
                "message": "Please try again later",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTTokenUserAuthentication])
def skill_offerings_detail_report(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    skill_offering_id = request.GET.get('skill_offering_id', None)
    view_all = request.GET.get('view_all', None)
    college_id = request.GET.get('college_id', None)
    branch_id = request.GET.get('branch_id', None)
    sem = request.GET.get('sem', None)
    zone_id = request.GET.get('zone_id', None)
    search_text = request.GET.get('search_text', None)

    student_query = {}
    search_query = []
    if search_text:
        search_query += Q(
            Q(student__roll_no__istartswith=search_text) |
            Q(student__invitation_id__istartswith=search_text) |
            Q(student__aadhar_number__istartswith=search_text) |
            Q(student__email__istartswith=search_text)
        )
    if college_id:
        student_query['student__college_id'] =college_id
    if branch_id:
        student_query['student__rbranch_id'] =branch_id
    if sem:
        student_query['student__sem'] = sem
    if zone_id:
        student_query['student__college__zone_id'] =zone_id

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20
    if not skill_offering_id:
        content = {
            "message": "Please provide skill_offering_id",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    try:
        if account_role == AccountRole.NM_ADMIN:
            skill_offering = SKillOffering.objects.get(id=skill_offering_id)
            enrollment_list = SKillOfferingEnrollment.objects.select_related('student', 'student__college').filter(
                *search_query,
                skill_offering_id=skill_offering.id,
                **student_query).exclude(student_id=None)
            subscribed_count = StudentCourse.objects.filter(course_id=skill_offering.lms_course_id, **student_query).exclude(student_id=None).distinct(
                'course_id',
                'student_id',
            ).count()

            enrollment_count = enrollment_list.distinct(
                'skill_offering_id',
                'student_id',
            ).count()
            total_count = enrollment_list.count()
            if view_all == '1':
                limit = total_count

            final_enrollment_list = []
            enrollment_list = enrollment_list.order_by('student__college__college_code', 'student__roll_no')
            for enrollment in enrollment_list[(page * limit): ((page * limit) + limit)]:
                student = enrollment.student
                is_subscribed = StudentCourse.objects.filter(course_id=skill_offering.lms_course_id, student_id=enrollment.student_id).exists()
                try:
                    progress_details = SKillOfferingEnrollmentProgress.objects.get(skill_offering_enrollment_id=enrollment.id)
                except SKillOfferingEnrollmentProgress.DoesNotExist:
                    progress_details = None
                except SKillOfferingEnrollmentProgress.MultipleObjectsReturned:
                    progress_details = SKillOfferingEnrollmentProgress.objects.filter(skill_offering_enrollment_id=enrollment.id).order_by('-created').first()
                temp = {
                    'is_subscribed': is_subscribed,
                    # Student details
                    'student_id': student.id,
                    'student_unique_id': student.invitation_id,
                    'full_name': student.aadhar_number,
                    'email': student.email,
                    'roll_no': student.roll_no,
                    'branch_id': student.rbranch_id,
                    'branch_name': student.rbranch.name if student.rbranch_id else None,
                    'sem': student.sem,
                    # College details
                    'college_id': student.college_id,
                    'college_name': student.college.college_name if student.college_id else None,
                    'college_code': student.college.college_code if student.college_id else None,
                    # Progress details
                    'progress_id': progress_details.id if progress_details else None,
                    'progress_percentage': progress_details.progress_percentage if progress_details else None,
                    'assessment_status': progress_details.assessment_status if progress_details else None,
                    'course_complete': progress_details.course_complete if progress_details else None,
                    'certificate_issued': progress_details.certificate_issued if progress_details else None,
                    'last_updated_at': progress_details.updated if progress_details else None,
                }
                final_enrollment_list.append(temp)
            content = {
                # Course details
                'skill_offering_id': skill_offering.id,
                'knowledge_partner_id': skill_offering.knowledge_partner_id,
                'knowledge_partner_name': skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else None,
                "course_name": skill_offering.course_name,
                "course_code": skill_offering.course_code,
                "sem": skill_offering.sem,
                "offering_type": skill_offering.offering_type,
                "offering_kind": skill_offering.offering_kind,
                "is_mandatory": skill_offering.is_mandatory,
                "mode_of_delivery": skill_offering.mode_of_delivery,
                "duration": skill_offering.duration,
                "outcomes": skill_offering.outcomes,
                "course_content": skill_offering.course_content,
                "description": skill_offering.description,
                "certification": skill_offering.certification,
                "cost": skill_offering.cost,
                "link": skill_offering.link,
                "job_category": skill_offering.job_category,
                "technology_id": skill_offering.technology_id,
                "technology_name": skill_offering.technology.name if skill_offering.technology_id else None,
                "sub_technology_id": skill_offering.sub_technology_id,
                "sub_technology_name": skill_offering.sub_technology.name if skill_offering.sub_technology_id else None,
                # Counters
                'enrollment_count': enrollment_count,
                'subscribed_count': subscribed_count,
                # Enrolled students list
                "enrolled_list": final_enrollment_list,
                "filters": {
                    'skill_offering_id': skill_offering_id,
                    'page': page,
                    'limit': limit,
                    'total_count': total_count,
                    'view_all': view_all,
                    'college_id': college_id,
                    'branch_id': branch_id,
                    'zone_id': zone_id,
                    'sem': sem,
                    'search_text': search_text,
                }
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')
        elif account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)

            skill_offering = SKillOffering.objects.get(id=skill_offering_id)
            enrollment_list = SKillOfferingEnrollment.objects.select_related('student').filter(
                *search_query,
                student__college_id=user_details.college_id,
                skill_offering_id=skill_offering.id, **student_query).exclude(student_id=None)
            subscribed_count = 0
            enrollment_count = enrollment_list.distinct(
                'skill_offering_id',
                'student_id',
            ).count()
            final_enrollment_list = []
            total_count = 0
            if enrollment_list:
                subscribed_count = StudentCourse.objects.select_related('student').filter(
                    student__college_id=user_details.college_id,
                    course_id=skill_offering.lms_course_id).exclude(student_id=None).distinct(
                    'course_id',
                    'student_id',
                ).count()
                total_count = enrollment_list.count()
                if view_all == '1':
                    limit = total_count

                enrollment_list = enrollment_list.order_by('student__roll_no')
                for enrollment in enrollment_list[(page * limit): ((page * limit) + limit)]:
                    student = enrollment.student
                    is_subscribed = StudentCourse.objects.filter(course_id=skill_offering.lms_course_id, student_id=enrollment.student_id).exists()
                    try:
                        progress_details = SKillOfferingEnrollmentProgress.objects.get(skill_offering_enrollment_id=enrollment.id)
                    except SKillOfferingEnrollmentProgress.DoesNotExist:
                        progress_details = None
                    temp = {
                        'is_subscribed': is_subscribed,
                        # Student details
                        'student_id': student.id,
                        'student_unique_id': student.invitation_id,
                        'full_name': student.aadhar_number,
                        'email': student.email,
                        'roll_no': student.roll_no,
                        'branch_id': student.rbranch_id,
                        'branch_name': student.rbranch.name if student.rbranch_id else None,
                        'sem': student.sem,
                        # College details
                        'college_id': student.college_id,
                        'college_name': student.college.college_name if student.college_id else None,
                        'college_code': student.college.college_code if student.college_id else None,
                        # Progress details
                        'progress_id': progress_details.id if progress_details else None,
                        'progress_percentage': progress_details.progress_percentage if progress_details else None,
                        'assessment_status': progress_details.assessment_status if progress_details else None,
                        'course_complete': progress_details.course_complete if progress_details else None,
                        'certificate_issued': progress_details.certificate_issued if progress_details else None,
                        'last_updated_at': progress_details.updated if progress_details else None,
                    }
                    final_enrollment_list.append(temp)

            content = {
                # Course details
                'skill_offering_id': skill_offering.id,
                'knowledge_partner_id': skill_offering.knowledge_partner_id,
                'knowledge_partner_name': skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else None,
                "course_name": skill_offering.course_name,
                "course_code": skill_offering.course_code,
                "sem": skill_offering.sem,
                "offering_type": skill_offering.offering_type,
                "offering_kind": skill_offering.offering_kind,
                "is_mandatory": skill_offering.is_mandatory,
                "mode_of_delivery": skill_offering.mode_of_delivery,
                "duration": skill_offering.duration,
                "outcomes": skill_offering.outcomes,
                "course_content": skill_offering.course_content,
                "description": skill_offering.description,
                "certification": skill_offering.certification,
                "cost": skill_offering.cost,
                "link": skill_offering.link,
                "job_category": skill_offering.job_category,
                "technology_id": skill_offering.technology_id,
                "technology_name": skill_offering.technology.name if skill_offering.technology_id else None,
                "sub_technology_id": skill_offering.sub_technology_id,
                "sub_technology_name": skill_offering.sub_technology.name if skill_offering.sub_technology_id else None,
                # Counters
                'enrollment_count': enrollment_count,
                'subscribed_count': subscribed_count,
                # Enrolled students list
                "enrolled_list": final_enrollment_list,
                "filters": {
                    'skill_offering_id': skill_offering_id,
                    'page': page,
                    'limit': limit,
                    'total_count': total_count,
                    'view_all': view_all,
                    'college_id': college_id,
                    'branch_id': branch_id,
                    'zone_id': zone_id,
                    'sem': sem,
                    'search_text': search_text,
                }
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')

        else:
            content = {
                "message": "You dont have the permission",
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    except SKillOffering.DoesNotExist:
        content = {
            "message": "Please provide valid skill_offering_id",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')




