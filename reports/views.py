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
from .models import DistrictReport, CollegeReport
from college.models import College
from django.db.models import F
from datarepo.views import get_class_list
# Create your views here.
import uuid

from django.conf import settings
from django.template.loader import get_template
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from nm_portal.config import Config

import csv

from io import StringIO
from datarepo.models import District
from student.models import Student
from lms.models import StudentCourse


@api_view(['GET'])
def list_district_reports(request):
    search_txt = request.GET.get('search_txt', None)
    college_type = request.GET.get('college_type', None)
    query = {}
    if search_txt:
        query['district__name__istartswith'] = search_txt
    if college_type:
        try:
            college_type = int(college_type)
            query['college_type_' + str(college_type) + "__gte"] = 1
        except:
            pass
    district_report_count = DistrictReport.objects.filter(**query).count()
    district_report_list = DistrictReport.objects.annotate(
        district_name=F('district__name')
    ).select_related('district').values(
        'district_id',
        'district_name',
        'total_no_of_colleges',
        'college_type_1',
        'college_type_2',
        'college_type_3',
        'college_type_4',
        'college_type_5',
    ).filter(**query).order_by(Lower('district_name'))
    content = {
        'district_reports_list': list(district_report_list),
        'district_reports_count': district_report_count,
        'search_txt': search_txt,
        'college_type': college_type
    }

    return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def list_college_reports(request):
    query = {}
    district_id = request.GET.get('district_id', None)
    if district_id:
        try:
            query['district_id'] = int(district_id)
        except:
            content = {
                'message': "Please provide valid district id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "Please provide district id"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    search_txt = request.GET.get('search_txt', None)
    affiliated_university_id = request.GET.get('affiliated_university_id', None)
    if affiliated_university_id:
        try:
            query['affiliated_university_id'] = int(affiliated_university_id)
        except:
            pass
    college_type = request.GET.get('college_type', None)
    if search_txt:
        query['district__name__istartswith'] = search_txt
    if college_type:
        try:
            college_type = int(college_type)
            query['college_type'] = college_type
        except:
            pass
    college_reports_count = CollegeReport.objects.filter(**query).count()
    college_reports_list = CollegeReport.objects.annotate(
        college_report_id=F('id'),
        affiliated_university_name=F('affiliated_university__name'),
        college_name=F('college__college_name')
    ).select_related('district').values(
        'college_report_id',
        'college_name',
        'college_type',
        'affiliated_university_name',
        'total_no_of_students',
    ).filter(**query).order_by(Lower('college_name'))
    content = {
        'college_reports_count': college_reports_count,
        'college_reports_list': list(college_reports_list),
        'search_txt': search_txt,
        'district_id': district_id,
        'affiliated_university_id': affiliated_university_id,
        'college_type': college_type
    }

    return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def college_details(request):
    query = {}
    college_report_id = request.GET.get('college_report_id', None)
    if college_report_id:
        try:
            query['college_report_id'] = int(college_report_id)

            get_college_report = CollegeReport.objects.get(id=college_report_id)
            get_college = get_college_report.college
            content = {
                'college_details': {
                    'college_name': get_college.college_name,
                    'college_code': get_college.college_code,
                    'email': get_college.email,
                    'is_mailed': get_college.is_mailed,
                    'mobile': get_college.mobile,
                    'college_type': get_college.college_type,
                    'affiliated_university_id': get_college.affiliated_university_id,
                    'affiliated_university': get_college.affiliated_university.name if get_college.affiliated_university_id else None,
                    'district_id': get_college.district_id,
                    'district': get_college.district.name if get_college.district_id else None,
                    'management_type': get_college.management_type,
                    'year_of_establishment': get_college.year_of_establishment,
                    'total_faculty_count': get_college.total_faculty_count,
                    'total_1st_year_students_count': get_college.total_1st_year_students_count,
                    'total_2nd_year_students_count': get_college.total_2nd_year_students_count,
                    'total_3rd_year_students_count': get_college.total_3rd_year_students_count,
                    'total_4th_year_students_count': get_college.total_4th_year_students_count,
                    'total_students_count': get_college.total_students_count,
                    'details_submitted_at': get_college.details_submitted_at,
                    # 'plot_no_and_street': get_college.plot_no_and_street,
                    # 'landmark': get_college.landmark,
                    # 'mandal': get_college.mandal,
                    # 'village_panchayat_colony': get_college.village_panchayat_colony,
                    # 'mandal_town_area': get_college.mandal_town_area,
                    'state': get_college.state,
                    'pincode': get_college.pincode,
                    'fax_number': get_college.fax_number,
                    'website_url': get_college.website_url,
                } if get_college else None,
                'total_no_of_students': get_college_report.total_no_of_students,
                'district_id': get_college_report.district_id,
                'district': get_college_report.district.name if get_college_report.district_id else None,
                'affiliated_university_id': get_college_report.affiliated_university_id,
                'affiliated_university': get_college_report.affiliated_university.name if get_college_report.affiliated_university_id else None,
            }

            return Response(content, status.HTTP_200_OK, content_type='application/json')
        except CollegeReport.DoesNotExist:
            content = {
                'message': "Please provide valid college_report_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except Exception as e:
            print(e)
            content = {
                'message': "Please provide valid college_report_id"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            'message': "Please provide college_report_id"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


def get_uuid():
    uid = uuid.uuid4()
    return str(uid)[::-1].replace("-", '')


@api_view(['POST'])
def upload_college_data(request):
    csv_file = request.FILES.get('csv_file', None)
    if csv_file:
        csv_file = csv_file.read().decode('utf-8')
        csv_data = csv.reader(StringIO(csv_file), delimiter=',')

        success_count = 0
        failed_count = 0
        for row in csv_data:
            # print(row)
            college_name = row[0]
            district = row[1]
            email = row[2]
            phone = row[3]
            college_type = row[4]
            if district:
                success_count += 1
                try:
                    get_district = District.objects.get(name__iexact=str(district).lower().strip())

                except District.DoesNotExist:

                    get_district = District.objects.create(name=str(district).lower().strip())

                COLLEGE_TYPE = None
                if college_type == 'ITI':
                    COLLEGE_TYPE = 3
                elif college_type == 'Engineering':
                    COLLEGE_TYPE = 2
                elif college_type == 'Polytechnic':
                    COLLEGE_TYPE = 4
                elif college_type == 'Arts & Science':
                    COLLEGE_TYPE = 1
                else:
                    COLLEGE_TYPE = 2
                if college_name and district:
                    try:
                        get_college = College.objects.get(
                            college_name__iexact=str(college_name).strip(),
                            email__iexact=str(email).strip(),
                        )
                        get_college.invitation_id = get_uuid()
                        get_college.district_id = get_district.id
                        get_college.email = email
                        get_college.mobile = phone
                        get_college.college_type = COLLEGE_TYPE
                        get_college.save()
                    except College.DoesNotExist:

                        get_college = College.objects.create(
                            college_name=str(college_name).strip(),
                            district_id=get_district.id,
                            email=str(email).strip(),
                            mobile=str(phone).strip(),
                            college_type=COLLEGE_TYPE,
                            invitation_id=get_uuid()
                        )
            else:
                print("College Name -> ", row)
                failed_count += 1

        content = {
            "message": 'uploaded successfully',
            'success_count': success_count,
            'failed_count': failed_count,
        }
    else:
        content = {
            "message": 'Please provide csv file'
        }

    return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def upload_college_data1(request):
    for district in District.objects.all():
        get_colleges = College.objects.filter(district_id=district.id)
        try:
            get_district_report = DistrictReport.objects.get(district_id=district.id)
        except:
            get_district_report = DistrictReport.objects.create(district_id=district.id)
        total_count = get_colleges.count()
        get_district_report.college_type_1 = get_colleges.filter(college_type=1).count()
        get_district_report.college_type_2 = get_colleges.filter(college_type=2).count()
        get_district_report.college_type_3 = get_colleges.filter(college_type=3).count()
        get_district_report.college_type_4 = get_colleges.filter(college_type=4).count()
        get_district_report.total_no_of_colleges = total_count
        get_district_report.total_no_of_colleges_invited = total_count
        get_district_report.save()

    content = {
        "message": 'Done'
    }
    return Response(content, status.HTTP_200_OK, content_type='application/json')


# removed auth
@api_view(['GET'])
def launch_stats(request):
    """
    1. total logged in students
    2. total invited students
    3. total students verified by colleges
    4. total online courses subcribed
    """
    # test
    return Response({
        "invited": Student.objects.filter(registration_status=11, is_mailed=1).count(),
        "first_time_logins": Student.objects.filter(payment_status=5).count(),
        "engineering_verified_count": Student.objects.filter(
            college__college_type=2,
            verification_status=0
        ).exclude(registration_status=11, is_mailed=1).count(),
        "course_subscription": StudentCourse.objects.filter(status=1).count(),
    }, status.HTTP_200_OK, content_type='application/json')
# te
