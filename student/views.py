from college.models import College
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
from datarepo.models import AccountRole
from .models import Student, StudentConcessions
import yaml
import jwt
from users.models import UserDetail
from django.conf import settings
from django.db.models.functions import Lower
from django.db.models import F
from nm_portal.config import Config
from datarepo.views import get_class_list
from django.db.models import Q, CharField, Value, F, Func
from django.db.models.functions import Concat
from datarepo.models import StudentRegistrationStatus
import random
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP_SSL as SMTP
import http.client
import json
from users.models import User, UserDetail
from datarepo.models import Branch
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress

"""
invite_student
--> POST --> invites a student to join the portal
        --> EMAIL WITH LINK WILL BE SENT TO STUDENT
--> access_levels
only college admin can do the invite the student

student_registration
--> GET with ID returns the registration details
--> POST will update the student
    creates a account
    and returns a token
--> access_levels
--> only student of his own record can finish the registration

student_subscription
--> GET with ID returns the subscription details
--> POST will update the subscription

students
--> GET returns students with filters
---> unpaid - True @TODO
    returns the unpaid students list
--> registered - True
    return the registered students list
--> access_levels
NMA & CA of his college students

student
-> GET with ID returns the student details
--> access_levels
NMA & CA of his college students & student of his own record
"""


# pranay now
@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def bulk_students_verify(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [
            AccountRole.COLLEGE_ADMIN,
            AccountRole.COLLEGE_ADMIN_STAFF]:
        if account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            student_ids = request.POST.get('student_ids', None)
            if student_ids is None:
                return Response({
                    'message': 'student_ids is manditory'
                }, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            student_ids = student_ids.split(',')
            student_data = Student.objects.filter(
                id__in=student_ids
            ).update(verification_status=True)
            return Response({
                'message': 'records have been verified'
            }, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def students(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    order_by_filter = []
    try:
        affiliated_university_id = request.GET.get(
            'affiliated_university_id', None)
        if affiliated_university_id:
            query['affiliated_university_id'] = int(affiliated_university_id)

        college_district_id = request.GET.get('college_district_id', None)
        if college_district_id:
            query['college__district__id'] = int(college_district_id)
        concessions = request.GET.get('concessions', None)
        if concessions:
            query['concessions'] = int(concessions)

        college_id = request.GET.get('college_id', None)
        if college_id:
            query['college_id'] = int(college_id)
        college_type = request.GET.get('college_type', None)
        if college_id:
            query['college_type'] = college_type

        current_district_id = request.GET.get('current_district_id', None)
        if current_district_id:
            query['current_district_id'] = int(current_district_id)

        permanent_district_id = request.GET.get('permanent_district_id', None)
        if permanent_district_id:
            query['permanent_district_id'] = int(permanent_district_id)

        management_type = request.GET.get('management_type', None)
        if management_type:
            query['management_type'] = int(management_type)

        is_pass_out = request.GET.get('is_pass_out', None)
        if is_pass_out:
            query['is_pass_out'] = int(is_pass_out)
        else:
            query['is_pass_out'] = 0

        college_type = request.GET.get('college_type', None)
        if college_type:
            query['college__college_type'] = int(college_type)

        subscription = request.GET.get('subscription', None)
        if subscription:
            query['subscription_status'] = int(subscription)

        registration_status = request.GET.get('status', None)
        if registration_status:
            query['registration_status'] = int(registration_status)

        year_of_study = request.GET.get('year_of_study', None)
        if year_of_study:
            query['year_of_study'] = int(year_of_study)

        verification_status = request.GET.get('verification_status', None)
        if verification_status:
            query['verification_status'] = int(verification_status)

        branch_id = request.GET.get('branch_id', None)
        if branch_id:
            query['rbranch_id'] = int(branch_id)
        sem = request.GET.get('sem', None)
        if sem:
            query['sem'] = int(sem)
        is_temporary_roll_number = request.GET.get(
            'is_temporary_roll_number', None)
        if is_temporary_roll_number:
            query['is_temporary_roll_number'] = int(is_temporary_roll_number)

        odb_college_name = request.GET.get('odb_college_name', None)
        if odb_college_name:
            order_by_filter.append(
                '-name' if odb_college_name == '1' else 'name')

        or_query_list = []
        search_txt = request.GET.get('search_txt', None)
        if search_txt:
            or_query_list.append(
                Q(
                    Q(roll_no__istartswith=search_txt)
                )
            )
    except Exception as e:
        content = {"message": "Please provide valid filters"}
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF,
                        AccountRole.FACULTY]:

        if account_role == AccountRole.NM_ADMIN:
            total_students_count = Student.objects.filter().count()
            total_unverified_students_count = Student.objects.filter(
                verification_status=0, is_pass_out=False).count()
        elif account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            print(user_details, user_details.college_id)
            query['college_id'] = user_details.college_id

            total_students_count = Student.objects.filter(
                college_id=user_details.college_id).count()
            total_unverified_students_count = Student.objects.filter(college_id=user_details.college_id,
                                                                     verification_status=0, is_pass_out=False).count()

        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            query['added_by_id'] = request.user.id
        elif account_role == AccountRole.FACULTY:
            user = User.objects.get(id=request.user.id)
            user_details = UserDetail.objects.get(user_id=request.user.id)

            username = user.username

            college_id=user_details.college_id
            get_college = College.objects.get(id=college_id)

            rep_username = ''

            if get_college.college_type == 2:
                    # Engineering
                rep_username = 'tnengg_fac' + str(get_college.college_code)
            elif get_college.college_type == 1:
                    # Arts & Science
                rep_username = 'tnas_fac' + str(get_college.college_code)
            elif get_college.college_type == 4:
                rep_username = 'tnpoly0_fac' + str(get_college.college_code)

            username = username.replace(rep_username, '')

            facid = int(username)
            query['id__in'] = SKillOfferingEnrollment.objects.values_list("student_id", flat=True).filter(faculty_id = facid)
            total_students_count = SKillOfferingEnrollment.objects.filter(faculty_id = facid).count()
            total_unverified_students_count = Student.objects.filter(**query,verification_status=0).count()
            
        students_count = Student.objects.filter(
            *or_query_list, **query).count()
        unverified_students_count = Student.objects.filter(*or_query_list, **query).filter(
            verification_status=0, is_pass_out=False).count()
        students_list = Student.objects.annotate(
            # district_name=F('college__district__name'),
            affiliated_university_name=F('affiliated_university__name'),
            status=F('registration_status'),
            district_name=F('current_district'),
            branch_name=F('rbranch__name'),
            full_name=Concat(F('first_name'), Value(" "), F('last_name')),
            college_name=F('college__college_name'),
            college_type=F('college__college_type'),
        ).select_related('affiliated_university', 'district',
                         'college').values(
            'id',
            'roll_no',
            'is_temporary_roll_number',
            'aadhar_number',
            'branch',
            'rbranch__name',
            'rbranch_id',
            'sem',
            'email',
            'college__college_code',
            'college__college_name',
            'college_type',
            'phone_number',
            'verification_status',
            'provisional_certificate',
            'certificate',

        ).filter(*or_query_list, **query).order_by(*order_by_filter, '-created')[
            (page * limit): ((page * limit) + limit)]

        # years_list = Student.objects.values(
        #     'year_of_study,
        # ).order_by('year_of_study')

        years_list = list(Student.objects.values_list(
            'year_of_study',
            flat=True).filter(year_of_study__isnull=False).order_by('year_of_study'))

        final_student_list = [
            {
                **record,
                'certificate': '/media/' + str(record['certificate']) if record['certificate'] else None,
                'provisional_certificate': '/media/' + str(record['provisional_certificate']) if record[
                    'provisional_certificate'] else None,
            } for record in students_list
        ]
        content = {
            'students_list': list(final_student_list),
            'total_count': students_count,
            'unverified_students_count': unverified_students_count,
            'total_students_count': total_students_count,
            'total_unverified_students_count': total_unverified_students_count,
            'page': page,
            'limit': limit,
            'filters': {
                'college_district_id': college_district_id,
                'branch_id': branch_id,
                'sem': sem,
                'permanent_district_id': permanent_district_id,
                'current_district_id': current_district_id,
                'affiliated_university_id': affiliated_university_id,
                'management_type': management_type,
                'college_type': college_type,
                'subscription': subscription,
                'status': registration_status,
                'concessions': concessions,
                'is_temporary_roll_number': is_temporary_roll_number,
                'years': list(set(years_list)) if years_list else [],
                'student_concessions': get_class_list(StudentConcessions)
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_students(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    order_by_filter = []
    try:
        affiliated_university_id = request.GET.get(
            'affiliated_university_id', None)
        if affiliated_university_id:
            query['affiliated_university_id'] = int(affiliated_university_id)

        college_district_id = request.GET.get('college_district_id', None)
        if college_district_id:
            query['college__district__id'] = int(college_district_id)
        concessions = request.GET.get('concessions', None)
        if concessions:
            query['concessions'] = int(concessions)

        college_id = request.GET.get('college_id', None)
        if college_id:
            query['college__id'] = int(college_id)

        current_district_id = request.GET.get('current_district_id', None)
        if current_district_id:
            query['current_district_id'] = int(current_district_id)

        permanent_district_id = request.GET.get('permanent_district_id', None)
        if permanent_district_id:
            query['permanent_district_id'] = int(permanent_district_id)

        management_type = request.GET.get('management_type', None)
        if management_type:
            query['management_type'] = int(management_type)
        is_temporary_roll_number = request.GET.get(
            'is_temporary_roll_number', None)
        if is_temporary_roll_number:
            query['is_temporary_roll_number'] = int(is_temporary_roll_number)

        is_pass_out = request.GET.get('is_pass_out', None)
        if is_pass_out:
            query['is_pass_out'] = int(is_pass_out)
        else:
            query['is_pass_out'] = 0

        college_type = request.GET.get('college_type', None)
        if college_type:
            query['degree'] = int(college_type)

        subscription = request.GET.get('subscription', None)
        if subscription:
            query['subscription_status'] = int(subscription)

        registration_status = request.GET.get('status', None)
        if registration_status:
            query['registration_status'] = int(registration_status)

        year_of_study = request.GET.get('year_of_study', None)
        if year_of_study:
            query['year_of_study'] = int(year_of_study)

        odb_college_name = request.GET.get('odb_college_name', None)
        if odb_college_name:
            order_by_filter.append(
                '-name' if odb_college_name == '1' else 'name')

        or_query_list = []
        search_txt = request.GET.get('search_txt', None)
        if search_txt:
            or_query_list.append(
                Q(
                    Q(first_name__istartswith=search_txt) |
                    Q(last_name__istartswith=search_txt) |
                    Q(email__istartswith=search_txt) |
                    Q(roll_no__istartswith=search_txt) |
                    Q(phone_number__istartswith=search_txt)
                )
            )

    except Exception as e:
        content = {"message": "Please provide valid filters"}
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF]:
        if account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            # print(user_details, user_details.college_id)
            query['college_id'] = user_details.college_id
        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            query['added_by_id'] = request.user.id
        students_count = Student.objects.filter(
            *or_query_list, **query).count()
        students_list = Student.objects.annotate(
            # district_name=F('college__district__name'),
            affiliated_university_name=F('affiliated_university__name'),
            status=F('registration_status'),
            district_name=F('current_district'),
            full_name=Concat(F('first_name'), Value(" "), F('last_name')),
            college_name=F('college__college_name'),
            college_type=F('college__college_type'),
        ).select_related('affiliated_university', 'district',
                         'college').values(
            'id',
            'invitation_id',
            'payment_status',
            'status',
            'full_name',
            'first_name',
            'last_name',
            'roll_no',
            'is_temporary_roll_number',
            'email',
            'caste',
            'concessions',
            'phone_number',
            'dob',
            'gender',
            'college_id',
            'college_name',
            'college_type',
            'district_name',
            'degree',
            'specialization',
            'affiliated_university_name',
            'specialization',
            'hall_ticket_number',
            'year_of_study',
            'year_of_graduation',
            'tenth_pass_out_year',
            'tenth_cgpa',
            'intermediate_pass_out_year',
            'is_first_year_in_degree',
            'certificate',
            'provisional_certificate',
            'is_pass_out',
            'current_graduation_cgpa',
            'has_backlogs',
            'subscription_status',
            'expiry_date',
            'created',
        ).filter(*or_query_list, **query).order_by(*order_by_filter, '-created')[
            (page * limit): ((page * limit) + limit)]

        # years_list = Student.objects.values(
        #     'year_of_study',
        # ).order_by('year_of_study')

        years_list = list(Student.objects.values_list(
            'year_of_study',
            flat=True).filter(year_of_study__isnull=False).order_by('year_of_study'))

        final_student_list = [
            {
                **record,
                'certificate': '/media/' + str(record['certificate']) if record['certificate'] else None,
                'provisional_certificate': '/media/' + str(record['provisional_certificate']) if record[
                    'provisional_certificate'] else None,
            } for record in students_list
        ]
        content = {
            'students_list': final_student_list,
            'total_count': students_count,
            'page': page,
            'limit': limit,
            'filters': {
                'college_district_id': college_district_id,
                'permanent_district_id': permanent_district_id,
                'current_district_id': current_district_id,
                'affiliated_university_id': affiliated_university_id,
                'management_type': management_type,
                'college_type': college_type,
                'subscription': subscription,
                'status': registration_status,
                'concessions': concessions,
                'years': list(set(years_list)) if years_list else [],
                'student_concessions': get_class_list(StudentConcessions)
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_students_with_basic_info(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    view_all = request.GET.get('view_all', None)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    order_by_filter = []
    mandatory_course_query = {}

    assessment_details = request.GET.get('assessment_details', None)
    try:
        affiliated_university_id = request.GET.get('affiliated_university_id', None)
        if affiliated_university_id:
            query['affiliated_university_id'] = int(affiliated_university_id)
        is_temporary_roll_number = request.GET.get('is_temporary_roll_number', None)
        if is_temporary_roll_number:
            query['is_temporary_roll_number'] = int(is_temporary_roll_number)

        college_district_id = request.GET.get('college_district_id', None)
        if college_district_id:
            query['college__district_id'] = int(college_district_id)
        concessions = request.GET.get('concessions', None)
        if concessions:
            query['concessions'] = int(concessions)

        college_id = request.GET.get('college_id', None)
        if college_id:
            query['college_id'] = int(college_id)
            mandatory_course_query['college_id'] = int(college_id)
        branch_id = request.GET.get('branch_id', None)
        if branch_id:
            query['rbranch_id'] = branch_id
        sem = request.GET.get('sem', None)
        if sem:
            query['sem'] = sem

        current_district_id = request.GET.get('current_district_id', None)
        if current_district_id:
            query['current_district_id'] = int(current_district_id)

        permanent_district_id = request.GET.get('permanent_district_id', None)
        if permanent_district_id:
            query['permanent_district_id'] = int(permanent_district_id)

        management_type = request.GET.get('management_type', None)
        if management_type:
            query['management_type'] = int(management_type)

        is_pass_out = request.GET.get('is_pass_out', None)
        if is_pass_out:
            query['is_pass_out'] = int(is_pass_out)
        else:
            query['is_pass_out'] = 0

        odb_college_name = request.GET.get('odb_college_name', None)
        if odb_college_name:
            order_by_filter.append('-name' if odb_college_name == '1' else 'name')

        or_query_list = []
        search_txt = request.GET.get('search_txt', None)
        if search_txt:
            or_query_list.append(
                Q(
                    Q(aadhar_number__istartswith=search_txt) |
                    Q(email__istartswith=search_txt) |
                    Q(roll_no__istartswith=search_txt)
                )
            )

    except Exception as e:
        content = {"message": "Please provide valid filters"}
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF,
                        AccountRole.FACULTY]:
        if account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            print(user_details, user_details.college_id)
            query['college_id'] = user_details.college_id
            mandatory_course_query['college_id'] = user_details.college_id
        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            query['added_by_id'] = request.user.id
            user_details = UserDetail.objects.get(user_id=request.user.id)
            print(user_details, user_details.college_id)
            query['college_id'] = user_details.college_id
            mandatory_course_query['college_id'] = user_details.college_id
        if account_role == AccountRole.FACULTY:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['college_id'] = user_details.college_id
            
            user = User.objects.get(id=request.user.id)
            username = user.username
                
            college_id=user_details.college_id
            get_college = College.objects.get(id=college_id)

            rep_username = ''

            if get_college.college_type == 2:
                    # Engineering
                rep_username = 'tnengg_fac' + str(get_college.college_code)
            elif get_college.college_type == 1:
                    # Arts & Science
                rep_username = 'tnas_fac' + str(get_college.college_code)
            elif get_college.college_type == 4:
                rep_username = 'tnpoly0_fac' + str(get_college.college_code)

            username = username.replace(rep_username, '')

            facid = int(username)
            query['id__in'] = SKillOfferingEnrollment.objects.values_list("student_id", flat=True).filter(faculty_id = facid)
            
        students_count = Student.objects.filter(*or_query_list, **query).count()
        if view_all == "1":
            limit = students_count
        students_list = Student.objects.annotate(name=F('aadhar_number'), branch_name=F('rbranch__name')).select_related('rbranch').filter(*or_query_list, **query).order_by(*order_by_filter, '-created')[
                        (page * limit): ((page * limit) + limit)]

        final_student_list = []
        mandatory_course_skill_offering_ids = []
        get_mandatory_course = None
        # if mandatory_course_id:
        #     try:
        #         get_mandatory_course = MandatoryCourse.objects.get(id=mandatory_course_id)
        #     except MandatoryCourse.DoesNotExist:
        #         content = {
        #             "message": "Please provide valid mandatory_course_id"
        #         }
        #         return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
        #
        # if mandatory_courses == "1":
        #     mandatory_course_skill_offering_ids = MandatoryCourse.objects.values_list('skill_offering_id', flat=True).filter(college_id=user_details.college_id)
        for std in students_list:
            get_college_mandatory_courses = MandatoryCourse.objects.filter(
                **mandatory_course_query,
                branch_id=std.rbranch_id,
                sem=std.sem
            )
            enrolled_course = SKillOfferingEnrollment.objects.filter(
                skill_offering_id__in=get_college_mandatory_courses.values_list('skill_offering_id', flat=True),
                student_id=std.id
            ).order_by('-created').first()
            mandatory_course_id = None
            mandatory_course_name = None
            manually_editable = None
            if enrolled_course:
                _mandatory_course = get_college_mandatory_courses.filter(skill_offering_id=enrolled_course.skill_offering_id).first()
                mandatory_course_id = _mandatory_course.id
                mandatory_course_name = _mandatory_course.skill_offering.course_name
                manually_editable = _mandatory_course.skill_offering.manually_editable

            temp_student = {
                "id": std.id,
                "name": std.name,
                "roll_no": std.roll_no,
                "phone_number": std.phone_number,
                "is_temporary_roll_number": std.is_temporary_roll_number,
                "email": std.email,
                "branch_name": std.branch_name,
                "sem": std.sem,
                'skill_offering_id': enrolled_course.skill_offering_id if enrolled_course else None,
                'ea_count': enrolled_course.skill_offering.ea_count if enrolled_course else None,
                'mandatory_course_id': mandatory_course_id,
                'mandatory_course_name': mandatory_course_name,
                'manually_editable' : manually_editable,
                'faculty_id' : enrolled_course.faculty.id if enrolled_course and enrolled_course.faculty else None
            }
            if assessment_details == '1':
                enrollment_progress = None
                if enrolled_course:
                    try:
                        enrollment_progress = SKillOfferingEnrollmentProgress.objects.get(
                            skill_offering_enrollment_id=enrolled_course.id
                        )
                    except SKillOfferingEnrollmentProgress.MultipleObjectsReturned:
                        enrollment_progress = SKillOfferingEnrollmentProgress.objects.filter(
                            skill_offering_enrollment_id=enrolled_course.id
                        ).order_by('-id').first()
                    except SKillOfferingEnrollmentProgress.DoesNotExist:
                        pass
                temp_student["skill_offering_enrollment_id"] = enrolled_course.id if enrolled_course else None
                temp_student["enrollment_progress_id"] = enrollment_progress.id if enrollment_progress else None
                temp_student["ea_1"] = enrollment_progress.ea_1 if enrollment_progress else None
                temp_student["ea_2"] = enrollment_progress.ea_2 if enrollment_progress else None
                temp_student["ea_3"] = enrollment_progress.ea_3 if enrollment_progress else None
                temp_student["ia_1"] = enrollment_progress.ia_1 if enrollment_progress else None
                temp_student["ia_2"] = enrollment_progress.ia_2 if enrollment_progress else None
                temp_student["ia_3"] = enrollment_progress.ia_3 if enrollment_progress else None
                temp_student["ia_4"] = enrollment_progress.ia_4 if enrollment_progress else None
                temp_student["ia_5"] = enrollment_progress.ia_5 if enrollment_progress else None
                temp_student["internal_marks"] = enrollment_progress.internal_marks if enrollment_progress and enrollment_progress.internal_marks else enrollment_progress.progress_percentage if enrollment_progress else None
                temp_student["external_marks"] = enrollment_progress.external_marks if enrollment_progress else None
                # temp_student["total_score"] = enrollment_progress.progress_percentage if enrollment_progress else None

            # if mandatory_course_id:
            #     skill_offering_id = None
            #     if get_mandatory_course:
            #         skill_offering_enrolled = SKillOfferingEnrollment.objects.filter(
            #             student_id=std.id,
            #             skill_offering_id=get_mandatory_course.skill_offering_id
            #         ).order_by('-created').first()
            #         skill_offering_id = skill_offering_enrolled.id if skill_offering_enrolled else None
            #
            #     # temp_student['mandatory_course_id'] = get_mandatory_course.id if get_mandatory_course else None
            #     temp_student['skill_offering_id'] = skill_offering_id
            # if mandatory_courses == '1':
            #     skill_offering_enrolled_course_list = SKillOfferingEnrollment.objects.filter(
            #         student_id=std.id,
            #         skill_offering_id__in=mandatory_course_skill_offering_ids
            #     )
            #     enrolled_course_list = []
            #     for course in skill_offering_enrolled_course_list:
            #         temp_course = {
            #             "skill_offering_enrollment_id": course.id,
            #             "knowledge_partner_id": course.knowledge_partner_id,
            #             "knowledge_partner": course.knowledge_partner.name if course.knowledge_partner_id else None,
            #             "skill_offering_id": course.skill_offering_id,
            #             "course_name": course.skill_offering.course_name if course.skill_offering_id else None,
            #             "course_code": course.skill_offering.course_code if course.skill_offering_id else None,
            #
            #         }
            #         enrolled_course_list.append(temp_course)
            #
            #     temp_student["enrolled_course_list"] = enrolled_course_list
            final_student_list.append(temp_student)
        # years_list = Student.objects.values(
        #     'year_of_study',
        # ).order_by('year_of_study')
        content = {
            'students_list': final_student_list,
            'total_count': students_count,
            'page': page,
            'limit': limit,
            'filters': {
                'college_id': college_id,
                'sem': sem,
                'branch_id': branch_id,
                'view_all': view_all,
                'assessment_details': assessment_details,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')



@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def update_student_course_assessment_details(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    skill_offering_enrollment_id = request.POST.get(
        'skill_offering_enrollment_id', None)
    # print(skill_offering_enrollment_id)
    ea_1 = request.POST.get('ea_1', None)
    ea_2 = request.POST.get('ea_2', None)
    ea_3 = request.POST.get('ea_3', None)
    internal_marks = request.POST.get('internal_marks', None)
    external_marks = request.POST.get('external_marks', None)

    query = {}
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF,
                        AccountRole.FACULTY]:
        if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
            pass
        elif account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['student__college_id'] = user_details.college_id
        elif account_role == AccountRole.FACULTY:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['student__college_id'] = user_details.college_id
        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['student__college_id'] = user_details.college_id
            query['student__added_by_id'] = request.user.id
        else:
            content = {
                "message": "You dont have the permission"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        try:
            skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                id=skill_offering_enrollment_id,
                **query
            )

            if ea_1 is None and ea_2 is None and ea_3 is None and internal_marks is None and external_marks is None:
                content = {
                    "message": "Please provide data"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                enrollment_progress_list = SKillOfferingEnrollmentProgress.objects.filter(
                    skill_offering_enrollment_id=skill_offering_enrollment_id
                )
                if enrollment_progress_list:
                    for record in enrollment_progress_list:
                        record.ea_1 = ea_1 if ea_1 else record.ea_1
                        record.ea_2 = ea_2 if ea_2 else record.ea_2
                        record.ea_3 = ea_3 if ea_3 else record.ea_3
                        record.internal_marks = internal_marks if internal_marks else record.internal_marks
                        record.external_marks = external_marks if external_marks else record.external_marks
                        record.save()
                else:
                    new_enrollment_progress = SKillOfferingEnrollmentProgress.objects.create(
                        skill_offering_enrollment_id=skill_offering_enrollment_id,
                        knowledge_partner_id=skill_offering_enrollment.knowledge_partner_id,
                        ea_1=ea_1 if ea_1 else None,
                        ea_2=ea_2 if ea_2 else None,
                        ea_3=ea_3 if ea_3 else None,
                        internal_marks=internal_marks if internal_marks else None,
                        external_marks=external_marks if external_marks else None
                    )
                content = {
                    "message": "Updated successfully"
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

        except SKillOfferingEnrollment.DoesNotExist:
            content = {
                "message": "Please provide valid skill_offering_enrollment_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:
            content = {
                "message": "Please try again later",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_branches(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    view_all = request.GET.get('view_all', None)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}

    college_id = request.GET.get('college_id', None)
    is_mandatory_course = request.GET.get('is_mandatory_course', None)
    if college_id:
        query['college_id'] = int(college_id)

    branch_query = {}
    branch_type = request.GET.get('branch_type', None)
    if branch_type:
        branch_query['branch_type'] = branch_type
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF,
                        AccountRole.FACULTY]:
        if account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['college_id'] = user_details.college_id
            if is_mandatory_course == '1':
                branch_query['id__in'] = MandatoryCourse.objects.values_list(
                    'branch_id', flat=True).filter(**query)
            else:
                branch_query['id__in'] = Student.objects.values_list(
                    'rbranch_id', flat=True).filter(**query)

        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            if is_mandatory_course == '1':
                student_branch_ids = Student.objects.values_list('rbranch_id', flat=True).filter(
                    **query,
                    added_by_id=request.user.id)
                branch_query['id__in'] = MandatoryCourse.objects.values_list('branch_id', flat=True).filter(
                    **query, branch_id__in=student_branch_ids)
            else:
                query['added_by_id'] = request.user.id
                branch_query['id__in'] = Student.objects.values_list(
                    'rbranch_id', flat=True).filter(**query)
                
        if account_role == AccountRole.FACULTY:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['college_id'] = user_details.college_id
            
            if is_mandatory_course == '1':
                branch_query['id__in'] = MandatoryCourse.objects.values_list(
                    'branch_id', flat=True).filter(**query)
            else:
                user = User.objects.get(id=request.user.id)
                username = user.username
                    
                college_id=user_details.college_id
                get_college = College.objects.get(id=college_id)

                rep_username = ''

                if get_college.college_type == 2:
                        # Engineering
                    rep_username = 'tnengg_fac' + str(get_college.college_code)
                elif get_college.college_type == 1:
                        # Arts & Science
                    rep_username = 'tnas_fac' + str(get_college.college_code)
                elif get_college.college_type == 4:
                    rep_username = 'tnpoly0_fac' + str(get_college.college_code)

                username = username.replace(rep_username, '')

                facid = int(username)
                query['id__in'] = SKillOfferingEnrollment.objects.values_list("student_id", flat=True).filter(faculty_id = facid)
                branch_query['id__in'] = Student.objects.values_list(
                    'rbranch_id', flat=True).filter(**query)
                    

        branches_count = Branch.objects.filter(**branch_query).count()
        if view_all == '1':
            limit = branches_count
        branch_list = Branch.objects.values('id', 'name', 'branch_type').filter(
            **branch_query)[(page * limit): ((page * limit) + limit)]

        # years_list = Student.objects.values(
        #     'year_of_study',
        # ).order_by('year_of_study')

        final_branch_list = list(branch_list)
        content = {
            'branch_list': final_branch_list,
            'total_count': branches_count,
            'page': page,
            'limit': limit,
            'filters': {
                'college_id': college_id,
                'view_all': view_all,
                'is_mandatory_course': is_mandatory_course,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_sem(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    query = {}
    is_mandatory_course = request.GET.get('is_mandatory_course', None)
    college_id = request.GET.get('college_id', None)
    if college_id:
        query['college_id'] = int(college_id)
    branch_id = request.GET.get('branch_id', None)

    branch_query = {}
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF,
                        AccountRole.FACULTY]:

        if account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['college_id'] = user_details.college_id

        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            students_sem_list = Student.objects.values_list(
                'sem', flat=True).filter(**query, added_by_id=request.user.id)
            query['sem__in'] = students_sem_list
        elif account_role == AccountRole.FACULTY:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['college_id'] = user_details.college_id
        
        if is_mandatory_course == '1':
            if branch_id:
                query['branch_id'] = branch_id
            sem_list = MandatoryCourse.objects.values_list(
                'sem', flat=True).filter(**query).exclude(sem=None)
        else:
            if branch_id:
                query['rbranch_id'] = branch_id
            if account_role == AccountRole.FACULTY:
                user = User.objects.get(id=request.user.id)
                username = user.username
                    
                college_id=user_details.college_id
                get_college = College.objects.get(id=college_id)

                rep_username = ''

                if get_college.college_type == 2:
                        # Engineering
                    rep_username = 'tnengg_fac' + str(get_college.college_code)
                elif get_college.college_type == 1:
                        # Arts & Science
                    rep_username = 'tnas_fac' + str(get_college.college_code)
                elif get_college.college_type == 4:
                    rep_username = 'tnpoly0_fac' + str(get_college.college_code)

                username = username.replace(rep_username, '')

                facid = int(username)
                query['id__in'] = SKillOfferingEnrollment.objects.values_list("student_id", flat=True).filter(faculty_id = facid)
        
            sem_list = Student.objects.values_list(
                'sem', flat=True).filter(**query).exclude(sem=None)

        content = {
            'sem_list': sorted(list(set(sem_list))) if sem_list else [],
            'filters': {
                'college_id': college_id,
                'branch_id': branch_id,
                'is_mandatory_course': is_mandatory_course,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def student(request, student_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    try:
        if request.method == 'GET':
            annotate_dict = {
                'affiliated_university_name': F('affiliated_university__name'),
                'status': F('registration_status'),
                'district_name': F('current_district'),
                'college_name': F('college__college_name'), }
            if account_role in [AccountRole.NM_ADMIN,
                                AccountRole.NM_ADMIN_STAFF, ]:
                get_student = Student.objects.annotate(**annotate_dict).select_related('college',
                                                                                       'affiliated_university').get(
                    id=student_id)
            elif account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
                user_details = UserDetail.objects.values('college_id').get(
                    user_id=request.user.id)
                get_student = Student.objects.annotate(**annotate_dict).select_related('college',
                                                                                       'affiliated_university').get(
                    id=student_id,
                    college_id=user_details['college_id'])
            else:
                content = {
                    "message": "You dont have the permission"
                }
                return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')

            content = {
                'student_details': {
                    'id': get_student.id,
                    'invitation_id': get_student.invitation_id,
                    'payment_status': get_student.payment_status,
                    'status': get_student.status,
                    'first_name': get_student.first_name,
                    'last_name': get_student.last_name,
                    'roll_no': get_student.roll_no,
                    'email': get_student.email,
                    'caste': get_student.caste,
                    'dob': get_student.phone_number,
                    'phone_number': get_student.phone_number,
                    'gender': get_student.gender,
                    'college_id': get_student.college_id,
                    'college_name': get_student.college.college_name if get_student.college_id else None,
                    'college_district_name': get_student.college.district.name if get_student.college.district_id else None if get_student.college_id else None,
                    'degree': get_student.degree,
                    'concessions': get_student.concessions,
                    'certificate': get_student.certificate.url if get_student.certificate else None,
                    'provisional_certificate': get_student.provisional_certificate.url if get_student.provisional_certificate else None,
                    'is_pass_out': get_student.is_pass_out,
                    'specialization': get_student.specialization,
                    'affiliated_university_name': get_student.affiliated_university.name if get_student.affiliated_university_id else None,
                    'hall_ticket_number': get_student.hall_ticket_number,
                    'year_of_study': get_student.year_of_study,
                    'year_of_graduation': get_student.year_of_graduation,
                    'tenth_pass_out_year': get_student.tenth_pass_out_year,
                    'tenth_cgpa': get_student.tenth_cgpa,
                    'intermediate_pass_out_year': get_student.intermediate_pass_out_year,
                    'is_first_year_in_degree': get_student.is_first_year_in_degree,
                    'current_graduation_cgpa': get_student.current_graduation_cgpa,
                    'has_backlogs': get_student.has_backlogs,
                    'subscription_status': get_student.subscription_status,
                    'expiry_date': get_student.expiry_date,
                    'created': get_student.created,
                    'current_address': {
                        'current_district': get_student.current_district,
                        'current_address': get_student.current_address,
                        # 'current_landmark': get_student.current_landmark,
                        # 'current_mandal': get_student.current_mandal,
                        'current_village': get_student.current_village,
                        'current_town_city': get_student.current_town_city,
                        'current_state': get_student.current_state,
                        'current_pincode': get_student.current_pincode,
                    },
                    'permanent_address': {
                        'permanent_district': get_student.permanent_district,
                        'permanent_address': get_student.permanent_address,
                        # 'permanent_landmark': get_student.permanent_landmark,
                        # 'permanent_mandal': get_student.permanent_mandal,
                        'permanent_village': get_student.permanent_village,
                        'permanent_town_city': get_student.permanent_town_city,
                        'permanent_state': get_student.permanent_state,
                        'permanent_pincode': get_student.permanent_pincode,
                    }
                },

            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')

        elif request.method == 'POST':
            if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
                user_details = UserDetail.objects.values('college_id').get(
                    user_id=request.user.id)
                get_student = Student.objects.get(
                    id=student_id, concessions=StudentConcessions.FILE_UPLOADED)

                concessions = request.POST.get('concessions', None)
                if concessions:
                    try:
                        concessions = int(concessions)
                        if concessions == 1:
                            # True
                            get_student.concessions = StudentConcessions.APPROVED
                            get_student.registration_status = StudentRegistrationStatus.APPROVED
                            get_student.save()
                            content = {
                                "message": "Approved successfully"
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')
                        elif concessions == 0:
                            get_student.concessions = StudentConcessions.REJECTED
                            get_student.save()
                            get_user_details = UserDetail.objects.select_related(
                                'user').get(student_id=get_student.id)
                            get_user_details.user.save()
                            content = {
                                "message": "Rejected successfully"
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')

                    except Exception as e:
                        print(e)
                content = {
                    "message": "Please provide valid concessions"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        else:
            content = {
                "message": "You dont have the permission"
            }
            return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    except Student.DoesNotExist:

        content = {
            "message": "Student deos not exist"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def upload_caste_certificate(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role == AccountRole.STUDENT:
        certificate = request.FILES.get('certificate', None)
        provisional_certificate = request.FILES.get(
            'provisional_certificate', None)
        if certificate:
            if certificate.__size > Config.FILE_UPLOAD_MAX_MEMORY_SIZE:
                user_details = UserDetail.objects.select_related(
                    'student').filter(user_id=request.user.id).first()
                if user_details:
                    if user_details.student_id:
                        if certificate:
                            user_details.student.certificate = certificate
                            user_details.student.concessions = StudentConcessions.FILE_UPLOADED
                        if provisional_certificate:
                            user_details.student.provisional_certificate = provisional_certificate
                            user_details.student.concessions = StudentConcessions.FILE_UPLOADED

                        user_details.student.save()
                        content = {
                            'message': "File uploaded successfully"
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            else:
                content = {
                    "message": "Please upload the certificate with max size 2Mb"
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

            content = {
                "message": "Please contact admin"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                "message": "Please upload the certificate"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have a permission"
        }
        return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')


##
@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def edit_student(request, student_id: int):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    regrex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    """
    :Public_endpoint
    :param request: invitation_id

    if invitation_id is valid from College Model with status=0
        if :POST - update_details
            1. update the details
            2. generate razor pay ID
            :return razor details

    else
        :return Invalid invitation_id
    """

    if student_id and account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.NM_ADMIN]:
        if request.method == 'POST':
            is_delete = request.POST.get('is_delete', None)
            is_send_invite = request.data.get('is_send_invite', None)
            is_send_invite = True if is_send_invite == 'true' else False
            if is_send_invite:
                try:
                    get_student = Student.objects.get(id=student_id)
                    try:
                        user_details = UserDetail.objects.get(
                            student_id=get_student.id, user_id__isnull=False)
                        user_info = user_details.user
                        username = user_info.username
                        password = str(random.randint(100000, 999999))
                        user_info.set_password(password)
                        user_info.save()
                    except UserDetail.DoesNotExist:
                        username_pref = ''
                        roll_no = (get_student.roll_no).replace(" ", '')
                        if get_student.is_temporary_roll_number:
                            username_pref = 'aut'
                        elif get_student.college.college_type == 1:
                            # username = 'au' + str(roll_no)
                            username_pref = 'as'
                        elif get_student.college.college_type == 2:
                            # username = 'au' + str(roll_no)
                            username_pref = 'au'
                        elif get_student.college.college_type == 4:
                            # username = 'p' + str(roll_no)
                            username_pref = 'p'

                        username = username_pref + str(roll_no).strip()
                        username = username.lower()
                        password = str(random.randint(100000, 999999))
                        try:
                            check_user = User.objects.get(username=username)
                            username = username_pref + \
                                str(get_student.college.college_code).strip(
                                ) + str(roll_no).strip()
                            try:
                                check_user = User.objects.get(
                                    username=username)
                                try:
                                    user_details = UserDetail.objects.get(
                                        user_id=check_user.id)
                                    content = {
                                        "message": "Duplicate user"
                                    }
                                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                                except UserDetail.DoesNotExist:
                                    user_details = UserDetail.objects.create(
                                        user_id=check_user.id,
                                        student_id=get_student.id,
                                    )
                                    user_info = check_user

                            except User.DoesNotExist:
                                user_info = User.objects.create(
                                    username=username,
                                    account_role=8)
                                user_details = UserDetail.objects.create(
                                    user_id=user_info.id,
                                    student_id=get_student.id,
                                )

                            # user_info.set_password(password)
                            # user_info.save()
                        except User.DoesNotExist:
                            user_info = User.objects.create(
                                username=username,
                                account_role=8)
                            user_info.save()
                            user_details = UserDetail.objects.create(
                                user_id=user_info.id,
                                student_id=get_student.id,
                            )
                        user_info.set_password(password)
                        user_info.save()
                        get_student.registration_status = 5
                        get_student.save()

                        user_details.save()
                        get_student.registration_status = 6
                        get_student.save()

                    """
                    """
                    SMTPserver = settings.CUSTOM_SMTP_HOST
                    sender = settings.CUSTOM_SMTP_SENDER

                    USERNAME = settings.CUSTOM_SMTP_USERNAME
                    PASSWORD = settings.CUSTOM_SMTP_PASSWORD

                    content = f"""\
                                                    Dear Team,

                                                    Greetings from  Naan Mudhalvan team. Thank you for your interest in Naan Mudhalvan programme

                                                    Please find your URL and login credentials for Naan Mudhalvan platform

                                                    URL to login : https://portal.naanmudhalvan.tn.gov.in/login
                                                                Username : {username}
                                                                Password : {password}

                                                    Please feel free to contact us on support email - support@naanmudhalvan.in

                                                    Thanks,
                                                    Naan Mudhalvan Team,
                                                    Tamil Nadu Skill Development Corporation


                                                    This is an automatically generated email from the Naan Mudhalvan Platform. Please do not reply to the sender of this email.


                                                    """

                    subject = "Invitation to Naan Mudhalvan"
                    text_subtype = 'plain'
                    msg = MIMEText(content, text_subtype)
                    msg['Subject'] = subject
                    # some SMTP servers will do this automatically, not all
                    msg['From'] = sender
                    msg['Date'] = formatdate(localtime=True)

                    conn = SMTP(host=SMTPserver, port=465)
                    conn.set_debuglevel(False)
                    conn.login(USERNAME, PASSWORD)
                    is_email_sent = None
                    try:
                        conn.sendmail(
                            sender, [get_student.email], msg.as_string())
                        is_email_sent = True
                    except Exception as e:
                        print(str(e))
                        is_email_sent = False
                    finally:
                        conn.quit()
                    is_sms_sent = None
                    if get_student.phone_number is not None:
                        try:
                            conn = http.client.HTTPConnection(
                                "digimate.airtel.in:15181")
                            payload = json.dumps({
                                "keyword": "DEMO",
                                "timeStamp": "1659688504",
                                "dataSet": [
                                    {
                                        "UNIQUE_ID": "16596885049652",
                                        "MESSAGE": "Hi  , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : " + username + " , password " + password + "\r\nNMGOVT",
                                        "OA": "NMGOVT",
                                        "MSISDN": "91" + str(get_student.phone_number),
                                        "CHANNEL": "SMS",
                                        "CAMPAIGN_NAME": "tnega_u",
                                        "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
                                        "USER_NAME": "tnega_tnsd",
                                        "DLT_TM_ID": "1001096933494158",
                                        "DLT_CT_ID": "1007269191406004910",
                                        "DLT_PE_ID": "1001857722001387178"
                                    }
                                ]
                            })
                            headers = {
                                'Content-Type': 'application/json'
                            }

                            conn.request(
                                "GET", "/BULK_API/InstantJsonPush", payload, headers)
                            res = conn.getresponse()
                            data = res.read()
                            sms_response = data.decode("utf-8")
                            if sms_response == 'true':
                                is_sms_sent = True
                            else:
                                is_sms_sent = False
                        except Exception as e:
                            is_sms_sent = False
                    get_student.registration_status = 11
                    get_student.save()
                    content = {
                        "message": "Invitation sent successfully",
                        "data": {
                            "is_email_sent": is_email_sent,
                            "is_sms_sent": is_sms_sent,
                            'username': username,
                            'password': password
                        }
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                except Student.DoesNotExist:
                    content = {
                        "message": "Student does not exist"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if is_delete == '1':
                try:
                    get_student = Student.objects.get(id=student_id)
                    get_user_details_list = UserDetail.objects.filter(
                        student_id=get_student.id)
                    for user_detail in get_user_details_list:
                        if user_detail.user_id:
                            user = user_detail.user
                            user.delete()
                        user_detail.delete()

                    get_student.delete()
                    content = {
                        "message": "Student deleted successfully"
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                except Student.DoesNotExist:
                    content = {
                        "message": "Student does not exist"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            # roll_no = request.POST.get('roll_no', None)
            phone_number = request.POST.get('phone_number', None)
            verification_status = request.POST.get('verification_status', None)

            is_pass_out = request.POST.get('is_pass_out', None)
            provisional_certificate = request.FILES.get(
                'provisional_certificate', None)

            caste = request.POST.get('caste', None)
            certificate = request.FILES.get('certificate', None)

            aadhar_number = request.POST.get('aadhar_number', None)
            sem = request.POST.get('sem', None)
            email = request.POST.get('email', None)
            dob = request.POST.get('dob', None)
            gender = request.POST.get('gender', None)
            # degree = request.POST.get('degree', None)
            specialization = request.POST.get('specialization', None)
            # district_id = request.POST.get('district_id', None)
            hall_ticket_number = request.POST.get('hall_ticket_number', None)
            year_of_study = request.POST.get('year_of_study', None)
            year_of_graduation = request.POST.get('year_of_graduation', None)

            # current_address = request.POST.get('current_address', None)
            current_address = request.POST.get('current_address', None)
            current_village = request.POST.get('current_village', None)
            current_town_city = request.POST.get('current_town_city', None)
            current_district = request.POST.get('current_district', None)
            current_state = request.POST.get('current_state', None)
            current_pincode = request.POST.get('current_pincode', None)

            permanent_address = request.POST.get('permanent_address', None)
            permanent_address = request.POST.get('permanent_address', None)
            # permanent_landmark = request.POST.get('permanent_landmark', None)
            # permanent_mandal = request.POST.get('permanent_mandal', None)
            permanent_village = request.POST.get('permanent_village', None)
            permanent_town_city = request.POST.get('permanent_town_city', None)
            permanent_district = request.POST.get('permanent_district', None)
            permanent_state = request.POST.get('permanent_state', None)
            permanent_pincode = request.POST.get('permanent_pincode', None)
            branch_id = request.POST.get('branch_id', None)
            roll_no = request.POST.get('roll_number', None)
            is_temporary_roll_number = request.POST.get(
                'is_temporary_roll_number', None)
            if verification_status:
                try:
                    verification_status = int(verification_status)
                except:
                    verification_status = None
            request_schema = '''
                first_name:
                    type: string
                    empty: true
                    required: false
                last_name:
                    type: string
                    empty: true
                    required: false
                aadhar_number:
                    type: string
                    empty: true
                    required: false
                verification_status:
                    type: string
                    empty: true
                    required: false
                sem:
                    type: string
                    empty: true
                    required: false
                phone_number:
                    type: string
                    empty: true
                    required: false
                    min: 10
                    max: 10
                gender:
                    type: string
                    empty: false
                    required: false
                caste:
                    type: string
                    empty: true
                    required: false
                is_pass_out:
                    type: string
                    empty: true
                    required: false
                provisional_certificate:
                    type: string
                    empty: true
                    required: false
                aadhar_number:
                    type: string
                    empty: true
                    required: false
                email:
                    type: string
                    empty: true
                    required: false
                dob:
                    type: string
                    empty: true
                    required: false
                specialization:
                    type: string
                    empty: true
                    required: false
                hall_ticket_number:
                    type: string
                    empty: true
                    required: false
                year_of_study:
                    type: string
                    empty: true
                    required: false
                    min: 4
                    max: 4
                year_of_graduation:
                    type: string
                    empty: true
                    required: false
                    min: 4
                    max: 4
                current_address:
                    type: string
                    empty: true
                    required: false
                roll_number:
                    type: string
                    empty: true
                    required: false
                is_temporary_roll_number:
                    type: string
                    empty: true
                    required: false
                    
                
                current_village:
                    type: string
                    empty: true
                    required: false
                    
                current_town_city:
                    type: string
                    empty: true
                    required: false
                    
                current_district:
                    type: string
                    empty: true
                    required: false
                    
                current_state:
                    type: string
                    empty: true
                    required: false
                    
                current_pincode:
                    type: string
                    empty: true
                    required: false
                    
                permanent_address:
                    type: string
                    empty: true
                    required: false
                    
                permanent_village:
                    type: string
                    empty: true
                    required: false
                    
                    
                permanent_town_city:
                    type: string
                    empty: true
                    required: false
                    
                permanent_district:
                    type: string
                    empty: true
                    required: false
                permanent_pincode:
                    type: string
                    empty: true
                    required: false
                permanent_state:
                    type: string
                    empty: true
                    required: false
                branch_id:
                    type: string
                    empty: true
                    required: false
                '''
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    if account_role == AccountRole.COLLEGE_ADMIN:
                        get_user_details = UserDetail.objects.select_related(
                            'college').get(user_id=request.user.id)
                        get_student = Student.objects.get(
                            id=student_id, college_id=get_user_details.college_id)
                    elif account_role == AccountRole.NM_ADMIN:
                        get_student = Student.objects.get(id=student_id)
                    else:
                        content = {
                            "message": "You dont have the permission",
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                    if roll_no is not None and str(roll_no).strip() != '':
                        check_roll_no_with_other_students = Student.objects.filter(
                            roll_no__iexact=roll_no, college_id=get_student.college_id).exclude(id=get_student.id).exists()
                        if check_roll_no_with_other_students:
                            content = {
                                "message": "Roll No is already exists to another student",
                            }
                            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                        get_student.roll_no = roll_no
                    if is_temporary_roll_number:
                        try:
                            is_temporary_roll_number = int(
                                is_temporary_roll_number)
                        except:
                            is_temporary_roll_number = None
                    try:
                        get_student.is_temporary_roll_number = is_temporary_roll_number if is_temporary_roll_number is not None else get_student.is_temporary_roll_number
                        get_student.verification_status = verification_status if verification_status else get_student.verification_status
                        get_student.rbranch_id = branch_id if branch_id is not None else get_student.rbranch_id
                        get_student.sem = sem if sem else get_student.sem
                        get_student.first_name = first_name if first_name else get_student.first_name
                        get_student.last_name = last_name if last_name else get_student.last_name
                        get_student.phone_number = phone_number if phone_number else get_student.phone_number
                        get_student.caste = caste if caste else get_student.caste
                        get_student.aadhar_number = aadhar_number if aadhar_number else get_student.aadhar_number
                        get_student.email = email if email else get_student.email
                        get_student.dob = dob if dob else get_student.dob
                        get_student.gender = gender if gender else get_student.gender
                        get_student.specialization = specialization if specialization else get_student.specialization
                        # current
                        get_student.current_address = current_address if current_address else get_student.current_address
                        get_student.current_village = current_village if current_village else get_student.current_village
                        get_student.current_town_city = current_town_city if current_town_city else get_student.current_town_city
                        get_student.current_state = current_state if current_state else get_student.current_state
                        get_student.current_district = current_district if current_district else get_student.current_district
                        # get_student.current_plot_no_and_street = current_plot_no_and_street
                        get_student.current_pincode = int(
                            current_pincode) if current_pincode else get_student.current_pincode
                        # Permanent
                        get_student.permanent_address = permanent_address if permanent_address else get_student.permanent_address
                        get_student.permanent_village = permanent_village if permanent_village else get_student.permanent_village
                        get_student.permanent_town_city = permanent_town_city if permanent_town_city else get_student.permanent_town_city
                        # get_student.permanent_village_panchayat_colony = permanent_village_panchayat_colony
                        # get_student.permanent_mandal_town_area = permanent_mandal_town_area
                        get_student.permanent_state = permanent_state if permanent_state else get_student.permanent_state
                        get_student.permanent_district = permanent_district if permanent_district else get_student.permanent_district
                        get_student.permanent_pincode = int(
                            permanent_pincode) if permanent_pincode else get_student.permanent_pincode

                        get_student.hall_ticket_number = hall_ticket_number if hall_ticket_number else get_student.hall_ticket_number
                        get_student.year_of_study = year_of_study if year_of_study else get_student.year_of_study
                        get_student.year_of_graduation = year_of_graduation if year_of_graduation else get_student.year_of_graduation
                        get_student.save()

                        content = {
                            "message": "updated successfully"
                        }
                        return Response(content, status.HTTP_200_OK, content_type='application/json')

                    except Exception as e:
                        content = {
                            "message": "Please provide valid data",
                            'error': str(e)
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Student.DoesNotExist:

                    content = {
                        "message": "invalid student ID"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                except Exception as e:
                    content = {
                        "message": "Please provide valid credentials",
                        'error': str(e)
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "Please provide student ID",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

# API for updating the internal_assesment and external_assesmnet scores


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def update_student_course_assessment_testscores(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    skill_offering_enrollment_id = request.POST.get(
        'skill_offering_enrollment_id', None)
    ea_1 = request.POST.get('ea_1', None)
    ea_2 = request.POST.get('ea_2', None)
    ea_3 = request.POST.get('ea_3', None)
    ia_1 = request.POST.get('ia_1', None)
    ia_2 = request.POST.get('ia_2', None)
    ia_3 = request.POST.get('ia_3', None)
    ia_4 = request.POST.get('ia_4', None)
    ia_5 = request.POST.get('ia_5', None)
    internal_marks = request.POST.get('internal_marks', None)
    external_marks = request.POST.get('external_marks', None)
    query = {}
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF,
                        AccountRole.FACULTY
                        ]:
        if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF, AccountRole.FACULTY]:
            pass
        elif account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['student__college_id'] = user_details.college_id
        elif account_role == AccountRole.FACULTY:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            # print(user_details)
            query['student__college_id'] = user_details.college_id
            query['student__added_by_id'] = request.user.id
            # print(query)
        else:
            # print("a")
            content = {
                "message": "You dont have the permission"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        try:
            skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                id=skill_offering_enrollment_id,
                **query
            )
            if ea_1 is None and ea_2 is None and ea_3 is None and ia_1 is None and ia_2 is None and ia_3 is None and ia_4 is None and ia_5 is None and external_marks is None:
                content = {
                    "message": "Please provide data"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                enrollment_progress_list = SKillOfferingEnrollmentProgress.objects.filter(
                    skill_offering_enrollment_id=skill_offering_enrollment_id
                )
                # print(enrollment_progress_list)
                if enrollment_progress_list:
                    for record in enrollment_progress_list:
                        record.ea_1 = ea_1 if ea_1 else record.ea_1
                        record.ea_2 = ea_2 if ea_2 else record.ea_2
                        record.ea_3 = ea_3 if ea_3 else record.ea_3
                        record.ia_1 = ia_1 if ia_1 else record.ia_1
                        record.ia_2 = ia_2 if ia_2 else record.ia_2
                        record.ia_3 = ia_3 if ia_3 else record.ia_3
                        record.ia_4 = ia_4 if ia_4 else record.ia_4
                        record.ia_5 = ia_5 if ia_5 else record.ia_5
                        record.internal_marks = internal_marks if internal_marks else record.internal_marks
                        record.external_marks = external_marks if external_marks else record.external_marks
                        record.save()
                else:
                    new_enrollment_progress = SKillOfferingEnrollmentProgress.objects.create(
                        skill_offering_enrollment_id=skill_offering_enrollment_id,
                        knowledge_partner_id=skill_offering_enrollment.knowledge_partner_id,
                        ea_1=ea_1 if ea_1 else None,
                        ea_2=ea_2 if ea_2 else None,
                        ea_3=ea_3 if ea_3 else None,
                        ia_1=ia_1 if ia_1 else None,
                        ia_2=ia_2 if ia_2 else None,
                        ia_3=ia_3 if ia_3 else None,
                        ia_4=ia_4 if ia_4 else None,
                        ia_5=ia_5 if ia_5 else None,
                        internal_marks=internal_marks if internal_marks else None,
                        external_marks=external_marks if external_marks else None,
                    )
                content = {
                    "message": "Updated successfully"
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

        except SKillOfferingEnrollment.DoesNotExist:
            content = {
                "message": "Please provide valid skill_offering_enrollment_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:
            content = {
                "message": "Please try again later",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        # print("b")
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


# Get API for Faculty Dashboard

@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def list_students_with_basic_info_faculty(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    view_all = request.GET.get('view_all', None)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    order_by_filter = []
    mandatory_course_query = {}

    assessment_details = request.GET.get('assessment_details', None)
    try:
        affiliated_university_id = request.GET.get(
            'affiliated_university_id', None)
        if affiliated_university_id:
            query['affiliated_university_id'] = int(affiliated_university_id)
        is_temporary_roll_number = request.GET.get(
            'is_temporary_roll_number', None)
        if is_temporary_roll_number:
            query['is_temporary_roll_number'] = int(is_temporary_roll_number)

        college_district_id = request.GET.get('college_district_id', None)
        if college_district_id:
            query['college__district_id'] = int(college_district_id)
        concessions = request.GET.get('concessions', None)
        if concessions:
            query['concessions'] = int(concessions)

        college_id = request.GET.get('college_id', None)
        if college_id:
            query['college_id'] = int(college_id)
            mandatory_course_query['college_id'] = int(college_id)
        branch_id = request.GET.get('branch_id', None)
        if branch_id:
            query['rbranch_id'] = branch_id
        sem = request.GET.get('sem', None)
        if sem:
            query['sem'] = sem

        current_district_id = request.GET.get('current_district_id', None)
        if current_district_id:
            query['current_district_id'] = int(current_district_id)

        permanent_district_id = request.GET.get('permanent_district_id', None)
        if permanent_district_id:
            query['permanent_district_id'] = int(permanent_district_id)

        management_type = request.GET.get('management_type', None)
        if management_type:
            query['management_type'] = int(management_type)

        is_pass_out = request.GET.get('is_pass_out', None)
        if is_pass_out:
            query['is_pass_out'] = int(is_pass_out)
        else:
            query['is_pass_out'] = 0

        odb_college_name = request.GET.get('odb_college_name', None)
        if odb_college_name:
            order_by_filter.append(
                '-name' if odb_college_name == '1' else 'name')

        or_query_list = []
        search_txt = request.GET.get('search_txt', None)
        if search_txt:
            or_query_list.append(
                Q(
                    Q(aadhar_number__istartswith=search_txt) |
                    Q(email__istartswith=search_txt) |
                    Q(roll_no__istartswith=search_txt)
                )
            )

    except Exception as e:
        content = {"message": "Please provide valid filters"}
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF]:
        if account_role == AccountRole.COLLEGE_ADMIN:
            # if account_role == AccountRole.FACULTY:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            # print(user_details, user_details.college_id)
            query['college_id'] = user_details.college_id
            mandatory_course_query['college_id'] = user_details.college_id
        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            query['added_by_id'] = request.user.id
            user_details = UserDetail.objects.get(user_id=request.user.id)
            # print(user_details, user_details.college_id)
            query['college_id'] = user_details.college_id
            mandatory_course_query['college_id'] = user_details.college_id
        students_count = Student.objects.filter(
            *or_query_list, **query).count()
        if view_all == "1":
            limit = students_count
        students_list = Student.objects.annotate(name=F('aadhar_number'), branch_name=F('rbranch__name')).select_related('rbranch').filter(*or_query_list, **query).order_by(*order_by_filter, '-created')[
            (page * limit): ((page * limit) + limit)]

        final_student_list = []
        mandatory_course_skill_offering_ids = []
        get_mandatory_course = None
        # if mandatory_course_id:
        #     try:
        #         get_mandatory_course = MandatoryCourse.objects.get(id=mandatory_course_id)
        #     except MandatoryCourse.DoesNotExist:
        #         content = {
        #             "message": "Please provide valid mandatory_course_id"
        #         }
        #         return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
        #
        # if mandatory_courses == "1":
        #     mandatory_course_skill_offering_ids = MandatoryCourse.objects.values_list('skill_offering_id', flat=True).filter(college_id=user_details.college_id)
        for std in students_list:
            get_college_mandatory_courses = MandatoryCourse.objects.filter(
                **mandatory_course_query,
                branch_id=std.rbranch_id,
                sem=std.sem
            )
            enrolled_course = SKillOfferingEnrollment.objects.filter(
                skill_offering_id__in=get_college_mandatory_courses.values_list(
                    'skill_offering_id', flat=True),
                student_id=std.id
            ).order_by('-created').first()
            mandatory_course_id = None
            if enrolled_course:
                _mandatory_course = get_college_mandatory_courses.filter(
                    skill_offering_id=enrolled_course.skill_offering_id).first()
                mandatory_course_id = _mandatory_course.id

            temp_student = {
                "id": std.id,
                "name": std.name,
                "roll_no": std.roll_no,
                "phone_number": std.phone_number,
                "is_temporary_roll_number": std.is_temporary_roll_number,
                "email": std.email,
                "branch_name": std.branch_name,
                "sem": std.sem,
                'skill_offering_id': enrolled_course.skill_offering_id if enrolled_course else None,
                'ea_count': enrolled_course.skill_offering.ea_count if enrolled_course else None,
                'mandatory_course_id': mandatory_course_id
            }
            if assessment_details == '1':
                enrollment_progress = None
                if enrolled_course:
                    try:
                        enrollment_progress = SKillOfferingEnrollmentProgress.objects.get(
                            skill_offering_enrollment_id=enrolled_course.id
                        )
                    except SKillOfferingEnrollmentProgress.MultipleObjectsReturned:
                        enrollment_progress = SKillOfferingEnrollmentProgress.objects.filter(
                            skill_offering_enrollment_id=enrolled_course.id
                        ).order_by('-id').first()
                    except SKillOfferingEnrollmentProgress.DoesNotExist:
                        pass
                temp_student["skill_offering_enrollment_id"] = enrolled_course.id if enrolled_course else None
                temp_student["enrollment_progress_id"] = enrollment_progress.id if enrollment_progress else None
                temp_student["ea_1"] = enrollment_progress.ea_1 if enrollment_progress else None
                temp_student["ea_2"] = enrollment_progress.ea_2 if enrollment_progress else None
                temp_student["ea_3"] = enrollment_progress.ea_3 if enrollment_progress else None
                temp_student["total_score"] = enrollment_progress.progress_percentage if enrollment_progress else None

            # if mandatory_course_id:
            #     skill_offering_id = None
            #     if get_mandatory_course:
            #         skill_offering_enrolled = SKillOfferingEnrollment.objects.filter(
            #             student_id=std.id,
            #             skill_offering_id=get_mandatory_course.skill_offering_id
            #         ).order_by('-created').first()
            #         skill_offering_id = skill_offering_enrolled.id if skill_offering_enrolled else None
            #
            #     # temp_student['mandatory_course_id'] = get_mandatory_course.id if get_mandatory_course else None
            #     temp_student['skill_offering_id'] = skill_offering_id
            # if mandatory_courses == '1':
            #     skill_offering_enrolled_course_list = SKillOfferingEnrollment.objects.filter(
            #         student_id=std.id,
            #         skill_offering_id__in=mandatory_course_skill_offering_ids
            #     )
            #     enrolled_course_list = []
            #     for course in skill_offering_enrolled_course_list:
            #         temp_course = {
            #             "skill_offering_enrollment_id": course.id,
            #             "knowledge_partner_id": course.knowledge_partner_id,
            #             "knowledge_partner": course.knowledge_partner.name if course.knowledge_partner_id else None,
            #             "skill_offering_id": course.skill_offering_id,
            #             "course_name": course.skill_offering.course_name if course.skill_offering_id else None,
            #             "course_code": course.skill_offering.course_code if course.skill_offering_id else None,
            #
            #         }
            #         enrolled_course_list.append(temp_course)
            #
            #     temp_student["enrolled_course_list"] = enrolled_course_list
            final_student_list.append(temp_student)
        # years_list = Student.objects.values(
        #     'year_of_study',
        # ).order_by('year_of_study')
        content = {
            'students_list': final_student_list,
            'total_count': students_count,
            'page': page,
            'limit': limit,
            'filters': {
                'college_id': college_id,
                'sem': sem,
                'branch_id': branch_id,
                'view_all': view_all,
                'assessment_details': assessment_details,
            }
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


# Assigning Faculty to the course


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def assign_faculty_to_course(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(
        token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    # data_list = request.POST.get(data)
    # print(data_list)
    # array = request.POST.getlist('data', None)
    # print(array)

    array = request.data['data']

    # skill_offering_enrollment_id = request.POST.get(
    #     'skill_enrollment_id', None)
    # student_id = request.POST.get(
    #     'student_id', None)
    # # print(skill_offering_enrollment_id)
    # faculty_id = request.POST.get('faculty_id', None)

    query = {}
    if account_role in [AccountRole.NM_ADMIN,
                        AccountRole.NM_ADMIN_STAFF,
                        AccountRole.COLLEGE_ADMIN,
                        AccountRole.COLLEGE_ADMIN_STAFF]:
        if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
            pass
        elif account_role == AccountRole.COLLEGE_ADMIN:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['student__college_id'] = user_details.college_id
        elif account_role == AccountRole.COLLEGE_ADMIN_STAFF:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            query['student__college_id'] = user_details.college_id
            query['student__added_by_id'] = request.user.id
        else:
            content = {
                "message": "You dont have the permission"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        try:
            # skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
            #     id=skill_offering_enrollment_id,
            #     **query
            # )
            # print(array)
            for i in array:
                print(i)
                skill_offering_enrollment_id = i['skill_enrollment_id']
                # print(skill_offering_enrollment_id)
                faculty_id = i['faculty_id']
                student_id = i['student_id']
                skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                    id=skill_offering_enrollment_id,
                )
                # print(skill_offering_enrollment)

                if faculty_id is None:
                    content = {
                        "message": "Please provide data"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                else:
                    enrollment_progress_list = SKillOfferingEnrollment.objects.filter(
                        skill_offering_id=skill_offering_enrollment_id
                    )
                    if enrollment_progress_list:
                        for record in enrollment_progress_list:
                            record.faculty_id = faculty_id if faculty_id else record.faculty_id
                            record.student_id = student_id if student_id else record.student_id
                            record.save()
                    else:
                        new_enrollment_progress = SKillOfferingEnrollment.objects.create(
                            skill_offering_id=skill_offering_enrollment_id,
                            knowledge_partner_id=skill_offering_enrollment.knowledge_partner_id,
                            faculty_id=faculty_id if faculty_id else None,
                            student_id=student_id if student_id else None,
                        )
            content = {
                "message": "Updated successfully"
            }
            return Response(content, status.HTTP_200_OK, content_type='application/json')

        except SKillOfferingEnrollment.DoesNotExist:
            content = {
                "message": "Please provide valid skill_offering_enrollment_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:
            content = {
                "message": "Please try again later",
                "error": str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
