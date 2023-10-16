from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from ..models import Specialisation, SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress, Technology, \
    SubTechnology, MandatoryCourse
from college.models import CollegeFaculty
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

from django.db import transaction as atomic_transaction


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def mandatory_courses_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF, AccountRole.FACULTY]:
        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            page = int(request.GET.get('page', 0))
            limit = int(request.GET.get('limit', 20))
            query = {
                'college_id': user_details.college_id
            }
            course_type = request.GET.get('course_type', None)
            if course_type:
                query['course_type'] = course_type
            branch_id = request.GET.get('branch_id', None)
            if branch_id:
                query['branch_id'] = branch_id
            sem = request.GET.get('sem', None)
            if sem:
                query['sem'] = sem
            mandatory_courses = MandatoryCourse.objects.select_related(
                'skill_offering', 'branch').filter(**query).distinct('skill_offering_id', 'branch_id', 'sem')

            total_count = mandatory_courses.count()
            final_list = []
            for _mandatory_course in mandatory_courses[(page * limit): ((page * limit) + limit)]:
                students_assigned_count = SKillOfferingEnrollment.objects.select_related('student', 'skill_offering').filter(
                    college_id=user_details.college_id,
                    student__sem=_mandatory_course.sem,
                    student__rbranch_id=_mandatory_course.branch_id,
                    skill_offering_id=_mandatory_course.skill_offering_id).count()
                temp = {
                    "mandatory_course_id": _mandatory_course.id,
                    "college_id": _mandatory_course.college_id,
                    "count": _mandatory_course.count,
                    'students_assigned_count': students_assigned_count,
                    "sem": _mandatory_course.sem,
                    "branch_id": _mandatory_course.branch_id,
                    "branch_name": _mandatory_course.branch.name if _mandatory_course.branch_id else None,
                    'skill_offering_id': _mandatory_course.skill_offering_id,
                    'skill_offering_course': _mandatory_course.skill_offering.course_name if _mandatory_course.skill_offering_id else None,
                    'course_type': _mandatory_course.course_type,
                    'is_unlimited': _mandatory_course.is_unlimited,
                    'created': _mandatory_course.created,
                    'updated': _mandatory_course.updated,
                }
                final_list.append(temp)

            context = {
                'mandatory_courses': final_list,
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'branch_id': branch_id,
                'sem': sem,
            }
            return Response(context, status.HTTP_200_OK, content_type='application/json')

        except UserDetail.DoesNotExist:

            return Response({'message': 'Please contact admin'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST', 'DELETE'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def mandatory_course(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    mandatory_course_id = request.POST.get('mandatory_course_id', None)
    student_id = request.POST.get('student_id', None)
    faculty_id = request.POST.get('faculty_id', None)
    if mandatory_course_id is None or student_id is None:
        return Response({'message': 'Please provide mandatory_course_id/ student_id'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            get_mandatory_course = MandatoryCourse.objects.get(
                id=mandatory_course_id, college_id=user_details.college_id)

            get_student = Student.objects.get(
                id=student_id, college_id=user_details.college_id)

            if request.method == 'POST':
                if faculty_id is None:
                    return Response({'message': 'Please provide faculty_id'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                
                get_faculty = CollegeFaculty.objects.get(
                	id=faculty_id, college_id=user_details.college_id)
					
                try:
                    get_std_enrolled_course = SKillOfferingEnrollment.objects.get(
                        student_id=student_id,
                        college_id=user_details.college_id,
                        skill_offering_id=get_mandatory_course.skill_offering_id,
                        faculty_id=faculty_id
                    )
                    return Response({'message': 'Course already assigned'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                except SKillOfferingEnrollment.DoesNotExist:

                    if get_mandatory_course.sem != get_student.sem:
                        context = {
                            "message": "Mandatory Course sem is not match with student sem"
                        }
                        return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                    get_skill_offering_enrollment_count = SKillOfferingEnrollment.objects.filter(
                        college_id=user_details.college_id,
                        student__sem=get_mandatory_course.sem,
                        student__rbranch_id=get_mandatory_course.branch_id,
                        skill_offering_id=get_mandatory_course.skill_offering_id
                    ).count()
                    if get_mandatory_course.count <= get_skill_offering_enrollment_count:
                        if not get_mandatory_course.is_unlimited:
                            return Response({'message': 'Assign count already reached'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                        else:
                            get_mandatory_course.count = get_skill_offering_enrollment_count + 1
                            get_mandatory_course.save()
                    new_std_enrolled_course = SKillOfferingEnrollment.objects.create(
                        student_id=student_id,
                        faculty_id=faculty_id,
                        college_id=user_details.college_id,
                        skill_offering_id=get_mandatory_course.skill_offering_id,
                        status=4,
                        is_mandatory=1,
                        knowledge_partner_id=get_mandatory_course.skill_offering.knowledge_partner_id if get_mandatory_course.skill_offering_id else None,
                        lms_course_id=get_mandatory_course.skill_offering.lms_course_id if get_mandatory_course.skill_offering_id else None
                    )
                    context = {
                        "message": "Enrolled successfully"
                    }
                    return Response(context, status.HTTP_200_OK, content_type='application/json')

            elif request.method == 'DELETE':
                try:
                    get_std_enrolled_course = SKillOfferingEnrollment.objects.get(
                        student_id=student_id,
                        college_id=user_details.college_id,
                        skill_offering_id=get_mandatory_course.skill_offering_id,
                    )
                    get_std_enrolled_course.delete()
                    return Response({'message': 'Enrolled course deleted successfully'}, status.HTTP_200_OK, content_type='application/json')
                except SKillOfferingEnrollment.DoesNotExist:

                    context = {
                        "message": "Enrolled Course not found"
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except UserDetail.DoesNotExist:
            return Response({'message': 'Please contact admin'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except MandatoryCourse.DoesNotExist:
            return Response({'message': 'Mandatory Course does not exist'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except Student.DoesNotExist:
            return Response({'message': 'Student does not exist'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def college_finish_allocation(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)

            if request.method == "GET":
                """
                1. ManCourse <— Branch <<— sem <— student (check with student allocation with Skill Offering Enrolment)
                2. False —>>
                    1. DB level update college_allocation = 0
                    2. Not allocated count
                """
                list_mandatory_courses = MandatoryCourse.objects.filter(
                    college_id=user_details.college_id)

                college_allocation = 1  # True
                not_allocated_students_count = 0
                branch_ids = list_mandatory_courses.values_list(
                    'branch_id', flat=True)
                branch_ids = list(set(list(branch_ids)))
                for branch_id in branch_ids:
                    sem_list_in_branch = list_mandatory_courses.filter(
                        branch_id=branch_id).values_list('sem', flat=True)
                    sem_list_in_branch = list(set(list(sem_list_in_branch)))
                    for sem in sem_list_in_branch:
                        skill_offering_ids = list_mandatory_courses.filter(
                            branch_id=branch_id, sem=sem).values_list('skill_offering_id', flat=True)
                        students_count = Student.objects.filter(
                            college_id=user_details.college_id,
                            rbranch_id=branch_id,
                            sem=sem
                        ).count()

                        skill_offering_enrollments_count = SKillOfferingEnrollment.objects.select_related('student').filter(
                            student__college_id=user_details.college_id,
                            student__rbranch_id=branch_id,
                            student__sem=sem,
                            skill_offering_id__in=skill_offering_ids
                        ).count()

                        if students_count > skill_offering_enrollments_count:
                            college_allocation = 0
                            not_allocated_students_count += students_count - skill_offering_enrollments_count
                            break

                if college_allocation == 0:
                    user_details.college.course_allocation = 0
                    user_details.college.save()

                context = {
                    "course_allocation": college_allocation,
                    "not_allocated_students_count": not_allocated_students_count,
                }
                return Response(context, status.HTTP_200_OK, content_type='application/json')

            elif request.method == "POST":
                """
                1. Check mandatory course allocation to all students and 
                2. if college_allocation = 1
                    1. update college Model
                3 else:
                    1. pass the students count
                """
                finished = request.POST.get('finished', None)
                if finished != '1':
                    context = {
                        "message": "Please provide valid finished"
                    }
                    return Response(context, status.HTTP_200_OK, content_type='application/json')

                list_mandatory_courses = MandatoryCourse.objects.filter(
                    college_id=user_details.college_id)

                college_allocation = 1  # True
                not_allocated_students_count = 0
                branch_ids = list_mandatory_courses.values_list(
                    'branch_id', flat=True)
                branch_ids = list(set(list(branch_ids)))
                for branch_id in branch_ids:
                    sem_list_in_branch = list_mandatory_courses.filter(
                        branch_id=branch_id).values_list('sem', flat=True)
                    sem_list_in_branch = list(set(list(sem_list_in_branch)))
                    for sem in sem_list_in_branch:
                        skill_offering_ids = list_mandatory_courses.filter(
                            branch_id=branch_id, sem=sem).values_list('skill_offering_id', flat=True)
                        students_count = Student.objects.filter(
                            college_id=user_details.college_id,
                            rbranch_id=branch_id,
                            sem=sem
                        ).count()

                        skill_offering_enrollments_count = SKillOfferingEnrollment.objects.select_related('student').filter(
                            student__college_id=user_details.college_id,
                            student__rbranch_id=branch_id,
                            student__sem=sem,
                            skill_offering_id__in=skill_offering_ids
                        ).count()

                        if students_count > skill_offering_enrollments_count:
                            college_allocation = 0
                            not_allocated_students_count += students_count - skill_offering_enrollments_count
                            break

                if college_allocation == 1:
                    user_details.college.course_allocation = 1
                    user_details.college.save()

                context = {
                    "course_allocation": college_allocation,
                    "not_allocated_students_count": not_allocated_students_count,
                }
                return Response(context, status.HTTP_200_OK, content_type='application/json')

            context = {
                "message": ""
            }
            return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except UserDetail.DoesNotExist:
            return Response({'message': 'Please contact admin'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
