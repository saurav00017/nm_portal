from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from .models import Specialisation, SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress, SKillOfferingEnrollmentCertificate, Technology, \
    SubTechnology, FeedBack
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

"""
specialisation
    technology
        subtechnology
"""


# TODO Add values for quries
@api_view(['GET'])
def specialisation_technologies(request):
    if request.method == 'GET':
        specialisations = Specialisation.objects.all()
        final = []
        # specialisation
        for temp_specialisation in specialisations:
            temp = {
                'specialisation_id': temp_specialisation.id,
                'specialisation_name': temp_specialisation.name,
            }
            technologies_q = SKillOffering.objects.filter(specialization__id=temp_specialisation.id).distinct(
                'technology_id')
            technologies_temp = []
            for technology in technologies_q:
                temp_tech = {
                    'technology_id': technology.technology.id,
                    'technology_name': technology.technology.name,
                }
                temp_groups = []
                for group in SubTechnology.objects.values('id', 'name').filter(
                        tech_id=technology.technology_id).order_by('name'):
                    temp_groups.append(
                        {
                            'sub_technology_id': group['id'],
                            'sub_technology_name': group['name'],
                        }
                    )
                temp_tech['sub_technologies'] = temp_groups
                technologies_temp.append(temp_tech)
            temp['technologies'] = technologies_temp
            final.append(temp)
        return Response(final, status=status.HTTP_200_OK)


# TODO Add values for quries
@api_view(['GET'])
def specialisation_technologies_1(request):
    if request.method == 'GET':
        specialisations = Specialisation.objects.values('id', 'name').all()
        specialisation_ids_list = specialisations.values_list('id', flat=True)
        skill_offering_list = SKillOffering.objects.select_related('technology', 'sub_technology').filter(
            specialization__id__in=specialisation_ids_list)
        final = []
        # specialisation
        for temp_specialisation in specialisations:
            temp = {
                'specialisation_id': temp_specialisation['id'],
                'specialisation_name': temp_specialisation['name'],
            }
            technologies_q = skill_offering_list.values(
                'technology_id',
                'technology__name'
            ).filter(specialization__id=temp_specialisation['id'])
            technologies_temp = []
            for technology in technologies_q:
                temp_tech = {
                    'technology_id': technology['technology_id'],
                    'technology_name': technology['technology__name'],
                }
                temp_groups = []
                for group in technologies_q.values(
                        'sub_technology_id',
                        'sub_technology__name',
                ).distinct('sub_technology_id'):
                    temp_groups.append(
                        {
                            'sub_technology_id': group['sub_technology_id'],
                            'sub_technology_name': group['sub_technology__name'],
                        }
                    )
                temp_tech['sub_technologies'] = temp_groups
                technologies_temp.append(temp_tech)
            temp['technologies'] = technologies_temp
            final.append(temp)
        return Response(final, status=status.HTTP_200_OK)


# TODO Add values for quries
@api_view(['GET'])
def skill_offerings(request):
    specialisation_id = request.GET.get('specialisation_id', None)
    technology_id = request.GET.get('technology_id', None)
    offering_type = request.GET.get('offering_type', None)
    offering_kind = request.GET.get('offering_kind', None)
    is_mandatory = request.GET.get('is_mandatory', None)
    sem = request.GET.get('sem', None)
    _status = request.GET.get('status', None)
    branch_id = request.GET.get('branch_id', None)
    year_of_study_id = request.GET.get('year_of_study_id', None)
    page = int(request.GET.get('page', 0))
    query = {}
    if _status is not None:
        query['status'] = _status
    if branch_id is not None:
        query['branch_id'] = branch_id
    if year_of_study_id is not None:
        query['year_of_study_id'] = year_of_study_id
    if sem is not None:
        query['sem'] = sem
    if is_mandatory is not None:
        query['is_mandatory'] = is_mandatory
    if specialisation_id is not None:
        query['specialization'] = specialisation_id
    if technology_id is not None:
        query['technology_id'] = technology_id
    if offering_type is not None:
        query['offering_type'] = offering_type
    if offering_kind is not None:
        query['offering_kind'] = offering_kind
    final_query = None
    limit = 25
    total_query = SKillOffering.objects.filter(**query)
    final_query = SKillOffering.objects.filter(**query)[(page * limit):(page * limit) + limit]
    return Response({
        'data': [
            {
                'skill_offering_id': skill_offering.id,
                'course_name': skill_offering.course_name,
                'knowledge_partner_name': skill_offering.knowledge_partner.name,
                'offering_kind': skill_offering.offering_kind,
                'offering_type': skill_offering.offering_type,
                'duration': skill_offering.duration,
                'certification': skill_offering.certification,
                'description': skill_offering.description,
            } for skill_offering in final_query
        ],
        'page': str(page),
        'count': final_query.count(),
        'total': total_query.count(),
        'total_pages': str(math.ceil(total_query.count() / limit) - 1)
    }, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def skill_offerings_detail(request):
    skill_offerings_id = request.GET.get('skill_offerings_id', None)
    if skill_offerings_id is None:
        return Response({
            'message': 'skill_offerings_id is required',
            'status': False
        }, status.HTTP_200_OK, content_type='application/json')
    try:
        skill_offering = SKillOffering.objects.get(id=skill_offerings_id)
        return Response({
            'skill_offering_id': skill_offering.id,
            'course_name': skill_offering.course_name,
            'description': skill_offering.description,
            'technology': skill_offering.technology.name if skill_offering.technology_id else None,
            'sub_technology': skill_offering.sub_technology.name if skill_offering.sub_technology_id else None,
            'year_of_study': skill_offering.year_of_study.values('year'),
            'mode_of_delivery': skill_offering.mode_of_delivery,
            'duration': skill_offering.duration,
            'certification': skill_offering.certification,
            'cost': skill_offering.cost,
            'outcomes': skill_offering.outcomes,
            'knowledge_partner_details': {
                'name': skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else None,
                'description': skill_offering.knowledge_partner.description,
                'logo': skill_offering.knowledge_partner.logo.url if skill_offering.knowledge_partner.logo else None,
                'website': skill_offering.knowledge_partner.website,
            },
            'offering_type': skill_offering.offering_type,
            'offering_kind': skill_offering.offering_kind,
            'is_lms': False if skill_offering.lms_course is None else True,
            'lms_course_id': '' if skill_offering.lms_course is None else skill_offering.lms_course_id,
            'link': skill_offering.link,
            'job_category': skill_offering.job_category,
        }, status.HTTP_200_OK,
            content_type='application/json')
    except SKillOffering.DoesNotExist:
        return Response({
            'message': 'skill_offerings_id does not exist',
            'status': False
        }, status.HTTP_200_OK, content_type='application/json')

# @api_view(['POST'])
# def upload_skill_offering_data(request):
#     csv_file = request.FILES.get('csv_file', None)
#     if csv_file:
#         csv_file = csv_file.read().decode('utf-8')
#         csv_data = csv.reader(StringIO(csv_file), delimiter=',')
#         for row in csv_data:
#             # print(row)
#
#             technology = row[1]
#             module_offering = row[2]
#             training_level = row[3]
#             specialization = row[10].split(',')
#             year_of_study = row[5]git p
#             mode_of_delivery = row[6]
#             duration = row[7]
#             certification = row[8]
#             # new
#             new_skill_offering = SKillOffering.objects.create(
#                 technology=technology,
#                 course_name=course_name,
#                 training_level=training_legvel,
#                 year_of_study=year_of_study,
#                 mode_of_delivery=mode_of_delivery,
#                 duration=duration,
#                 certification=certification,
#                 cost=cost,
#             )
#             new_skill_offering.save()
#             for x in specialization:
#                 specialization_info = Specialisation.objects.get(id=int(x))
#                 new_skill_offering.specialization.add(specialization_info)
#                 new_skill_offering.save()
#         content = {
#             "message": 'uploaded successfully',
#         }
#     else:
#         content = {
#             "message": 'Please provide csv file'
#         }
#
#     return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['POST', 'PATCH'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def skill_offering(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    if account_role == AccountRole.NM_ADMIN:
        knowledge_partner_id = request.POST.get('knowledge_partner_id', None)
        technology_id = request.POST.get('technology_id', None)
        course_code = request.POST.get('course_code', None)
        course_name = request.POST.get('course_name', None)
        sub_technology_id = request.POST.get('sub_technology_id', None)
        specialization_id = request.POST.get('specialization_id', None)
        branch_id = request.POST.get('branch_id', None)
        year_of_study_id = request.POST.get('year_of_study_id', None)
        mode_of_delivery = request.POST.get('mode_of_delivery', None)
        duration = request.POST.get('duration', None)
        outcomes = request.POST.get('outcomes', None)
        course_content = request.POST.get('course_content', None)
        description = request.POST.get('description', None)
        certification = request.POST.get('certification', None)
        cost = request.POST.get('cost', None)
        link = request.POST.get('link', None)
        is_mandatory = request.POST.get('is_mandatory', None)
        sem = request.POST.get('sem', None)
        offering_type = request.POST.get('offering_type', None)
        offering_kind = request.POST.get('offering_kind', None)
        job_category = request.POST.get('job_category', None)
        lms_course_code = request.POST.get('lms_course_code', None)
        skill_offering_status = request.POST.get('status', None)

        if request.method == 'POST':
            request_schema = '''
                knowledge_partner_id:
                    type: string
                    empty: false
                    required: true
                technology_id:
                    type: string
                    empty: false
                    required: true
                course_code:
                    type: string
                    empty: false
                    required: true
                course_name:
                    type: string
                    empty: false
                    required: true 
                sub_technology_id:
                    type: string
                    empty: false
                    required: true
                    
                specialization_id:
                    type: string
                    empty: false
                    required: true
                    
                branch_id:
                    type: string
                    empty: false
                    required: true
                year_of_study_id:
                    type: string
                    empty: false
                    required: true
                mode_of_delivery:
                    type: string
                    empty: false
                    required: true
                duration:
                    type: string
                    empty: false
                    required: true
                outcomes:
                    type: string
                    empty: false
                    required: true
                course_content:
                    type: string
                    empty: false
                    required: true
                description:
                    type: string
                    empty: false
                    required: true
                certification:
                    type: string
                    empty: false
                    required: true
                cost:
                    type: string
                    empty: false
                    required: true
                link:
                    type: string
                    empty: false
                    required: true
                is_mandatory:
                    type: string
                    empty: false
                    required: true
                sem:
                    type: string
                    empty: false
                    required: true
                offering_type:
                    type: string
                    empty: false
                    required: true
                offering_kind:
                    type: string
                    empty: false
                    required: true
                job_category:
                    type: string
                    empty: false
                    required: true
                    
                '''
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    knowledge_partner = KnowledgePartner.objects.get(id=knowledge_partner_id)
                    technology = Technology.objects.get(id=technology_id)
                    sub_technology = SubTechnology.objects.get(id=sub_technology_id)
                    specialization = Specialisation.objects.get(id=specialization_id)
                    branch = Branch.objects.get(id=branch_id)
                    year_of_study = YearOfStudy.objects.get(id=year_of_study_id)
                    lms_course = None
                    if lms_course_code:
                        lms_course = LMSCourse.objects.get(course_unique_code=lms_course_code)
                    new_skill_offering = SKillOffering.objects.create(
                        knowledge_partner_id=knowledge_partner_id,
                        technology_id=technology_id,
                        course_code=course_code,
                        course_name=course_name,
                        sub_technology_id=sub_technology_id,
                        specialization_id=specialization_id,
                        branch_id=branch_id,
                        year_of_study_id=year_of_study_id,
                        mode_of_delivery=mode_of_delivery,
                        duration=duration,
                        outcomes=outcomes,
                        course_content=course_content,
                        description=description,
                        certification=certification,
                        cost=cost,
                        link=link,
                        is_mandatory=is_mandatory,
                        sem=sem,
                        lms_course_id=lms_course.id if lms_course else None,
                        offering_type=offering_type,
                        offering_kind=offering_kind,
                        job_category=job_category
                    )
                    context = {
                        'message': "Skill Offering created successfully",
                        'skill_offering_id': new_skill_offering.id
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except LMSCourse.DoesNotExist:
                    context = {
                        'message': "LMS Course does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except KnowledgePartner.DoesNotExist:
                    context = {
                        'message': "Knowledge Partner does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Technology.DoesNotExist:
                    context = {
                        'message': "Technology does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except SubTechnology.DoesNotExist:
                    context = {
                        'message': "Sub Technology does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Specialisation.DoesNotExist:
                    context = {
                        'message': "Specialisation does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Branch.DoesNotExist:
                    context = {
                        'message': "Branch does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except YearOfStudy.DoesNotExist:
                    context = {
                        'message': "YearOfStudy does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Exception as e:
                    print("Error - skill_offering")
                    content = {
                        'message': "Please try again later",
                        "error": str(e)
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        elif request.method == 'PATCH':
            skill_offering_id = request.POST.get('skill_offering_id', None)
            request_schema = '''
                skill_offering_id:
                    type: string
                    empty: false
                    required: true
                knowledge_partner_id:
                    type: string
                    empty: true
                    required: false
                technology_id:
                    type: string
                    empty: true
                    required: false
                course_code:
                    type: string
                    empty: true
                    required: false
                course_name:
                    type: string
                    empty: true
                    required: false
                sub_technology_id:
                    type: string
                    empty: true
                    required: false
                    
                specialization_id:
                    type: string
                    empty: true
                    required: false
                    
                branch_id:
                    type: string
                    empty: true
                    required: false
                year_of_study_id:
                    type: string
                    empty: true
                    required: false
                mode_of_delivery:
                    type: string
                    empty: true
                    required: false
                duration:
                    type: string
                    empty: true
                    required: false
                outcomes:
                    type: string
                    empty: true
                    required: false
                course_content:
                    type: string
                    empty: true
                    required: false
                description:
                    type: string
                    empty: true
                    required: false
                certification:
                    type: string
                    empty: true
                    required: false
                cost:
                    type: string
                    empty: true
                    required: false
                link:
                    type: string
                    empty: true
                    required: false
                is_mandatory:
                    type: string
                    empty: true
                    required: false
                sem:
                    type: string
                    empty: true
                    required: false
                offering_type:
                    type: string
                    empty: true
                    required: false
                offering_kind:
                    type: string
                    empty: true
                    required: false
                job_category:
                    type: string
                    empty: true
                    required: false
                status:
                    type: string
                    empty: true
                    required: false
                    
                '''
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    get_skill_offering = SKillOffering.objects.get(id=skill_offering_id)
                    if knowledge_partner_id:
                        knowledge_partner = KnowledgePartner.objects.get(id=knowledge_partner_id)
                    if technology_id:
                        technology = Technology.objects.get(id=technology_id)
                    if sub_technology_id:
                        sub_technology = SubTechnology.objects.get(id=sub_technology_id)
                    if specialization_id:
                        specialization = Specialisation.objects.get(id=specialization_id)
                    if branch_id:
                        branch = Branch.objects.get(id=branch_id)
                    if year_of_study_id:
                        year_of_study = YearOfStudy.objects.get(id=year_of_study_id)
                    lms_course = None
                    if lms_course_code:
                        lms_course = LMSCourse.objects.get(course_unique_code=lms_course_code)

                    get_skill_offering.knowledge_partner_id = knowledge_partner_id if knowledge_partner_id else get_skill_offering.knowledge_partner_id
                    get_skill_offering.technology_id = technology_id if technology_id else get_skill_offering.technology_id
                    get_skill_offering.course_code = course_code if course_code else get_skill_offering.course_code
                    get_skill_offering.course_name = course_name if course_name else get_skill_offering.course_name
                    get_skill_offering.sub_technology_id = sub_technology_id if sub_technology_id else get_skill_offering.sub_technology_id
                    get_skill_offering.specialization_id = specialization_id if specialization_id else get_skill_offering.specialization_id
                    get_skill_offering.branch_id = branch_id if branch_id else get_skill_offering.branch_id
                    get_skill_offering.year_of_study_id = year_of_study_id if year_of_study_id else get_skill_offering.year_of_study_id
                    get_skill_offering.mode_of_delivery = mode_of_delivery if mode_of_delivery else get_skill_offering.mode_of_delivery
                    get_skill_offering.duration = duration if duration else get_skill_offering.duration
                    get_skill_offering.outcomes = outcomes if outcomes else get_skill_offering.outcomes
                    get_skill_offering.course_content = course_content if course_content else get_skill_offering.course_content
                    get_skill_offering.description = description if description else get_skill_offering.description
                    get_skill_offering.certification = certification if certification else get_skill_offering.certification
                    get_skill_offering.cost = cost if cost else get_skill_offering.cost
                    get_skill_offering.link = link if link else get_skill_offering.link
                    get_skill_offering.is_mandatory = is_mandatory if is_mandatory else get_skill_offering.is_mandatory
                    get_skill_offering.sem = sem if sem else get_skill_offering.sem
                    get_skill_offering.lms_course_id = lms_course.id if lms_course else None if knowledge_partner_id else get_skill_offering.lms_course_id
                    get_skill_offering.offering_type = offering_type if offering_type else get_skill_offering.offering_type
                    get_skill_offering.offering_kind = offering_kind if offering_kind else get_skill_offering.offering_kind
                    get_skill_offering.job_category = job_category if job_category else get_skill_offering.job_category
                    get_skill_offering.status = skill_offering_status if skill_offering_status else get_skill_offering.status
                    get_skill_offering.save()
                    context = {
                        'message': "Skill Offering updated successfully",
                        'skill_offering_id': get_skill_offering.id
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except LMSCourse.DoesNotExist:
                    context = {
                        'message': "LMS Course does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except KnowledgePartner.DoesNotExist:
                    context = {
                        'message': "Knowledge Partner does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Technology.DoesNotExist:
                    context = {
                        'message': "Technology does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except SubTechnology.DoesNotExist:
                    context = {
                        'message': "Sub Technology does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Specialisation.DoesNotExist:
                    context = {
                        'message': "Specialisation does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Branch.DoesNotExist:
                    context = {
                        'message': "Branch does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except YearOfStudy.DoesNotExist:
                    context = {
                        'message': "YearOfStudy does not exist",
                    }
                    return Response(context, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Exception as e:
                    print("Error - skill_offering")
                    content = {
                        'message': "Please try again later",
                        "error": str(e)
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

            return Response({'message': 'skill_offering_id is Invalid', 'enrollment': 'false'}, status.HTTP_200_OK,
                            content_type='application/json')
    else:
        return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def skill_offering_dropdowns(request):
    kp_id = request.GET.get('knowledge_partner_id')
    lms_courses = []
    if kp_id:
        try:
            _kp = KnowledgePartner.objects.get(id=kp_id)
            lms_courses = list(LMSCourse.objects.values(
                'id', 'course_unique_code', 'course_name', 'course_type'
            ).filter(
                lms_client_id=_kp.lms_client_id
            ))
        except KnowledgePartner.DoesNotExist:
            return Response({'message': 'Please provide valid knowledge_partner_id'}, status.HTTP_400_BAD_REQUEST,
                            content_type='application/json')
    content = {
        'technology': [{
            'id': x.id,
            'name': x.name,
            'sub_technology': [{
                'id': sub.id,
                'name': sub.name,
            } for sub in SubTechnology.objects.filter(tech_id=x.id).order_by('name')]
        } for x in Technology.objects.all().order_by('name')],

        'specialization': [{
            'id': sub.id,
            'name': sub.name,
        } for sub in Specialisation.objects.order_by('name').all()],
        'branch': [{
            'id': branch.id,
            'name': branch.name,
        } for branch in Branch.objects.order_by('name').all()],
        'year_of_study': [{
            'id': year.id,
            'name': year.year,
        } for year in YearOfStudy.objects.all()],
        'lms_courses': lms_courses
    }
    return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['POST', 'GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def skill_offering_enrollment(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    if request.method == 'POST':
        if account_role == AccountRole.STUDENT:
            skill_offering_id = request.POST.get('skill_offering_id', None)
            if skill_offering_id is None:
                return Response({'message': 'skill_offering_id is Invalid'}, status.HTTP_200_OK,
                                content_type='application/json')
            try:
                skill_offering_info = SKillOffering.objects.get(id=skill_offering_id)
                # get count of enrollments if less then 5 then make enrollment to new
                student_info = UserDetail.objects.get(user_id=request.user.id)

                student_enrolled_courses = SKillOfferingEnrollment.objects.filter(
                    student_id=student_info.student_id
                )
                # check what kind and type of skill offering is it
                # online free
                if skill_offering_info.offering_type == 1 and skill_offering_info.offering_kind == 0:
                    try:
                        check_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                            student_id=student_info.student_id,
                            skill_offering_id=skill_offering_info.id)
                        return Response({'message': 'You have already enrolled in this course'}, status.HTTP_200_OK,
                                        content_type='application/json')
                    except SKillOfferingEnrollment.DoesNotExist:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                            student_id=student_info.student_id,
                            college_id=student_info.student.college_id,
                            knowledge_partner_id=skill_offering_info.knowledge_partner.id,
                            skill_offering_id=skill_offering_info.id,
                            status=4,
                            offering_type=skill_offering_info.offering_type)
                        new_skill_offering_enrollment.save()
                        return Response({'message': 'Course enrollment request has been submitted',
                                         'enrollment': 'true',
                                         'enrollment_status': 4
                                         },
                                        status.HTTP_200_OK,
                                        content_type='application/json')
                # online paid
                elif skill_offering_info.offering_type == 1 and skill_offering_info.offering_kind == 1:
                    try:
                        check_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                            student_id=student_info.student_id,
                            skill_offering_id=skill_offering_info.id)
                        return Response({'message': 'You have already enrolled to this course', 'enrollment': 'false'},
                                        status.HTTP_200_OK,
                                        content_type='application/json')
                    except SKillOfferingEnrollment.DoesNotExist:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                            student_id=student_info.student_id,
                            college_id=student_info.student.college_id,
                            knowledge_partner_id=skill_offering_info.knowledge_partner.id,
                            skill_offering_id=skill_offering_info.id,
                            status=0,
                            offering_type=skill_offering_info.offering_type)  # approved / active status
                        new_skill_offering_enrollment.save()
                        return Response({'message': 'Course enrollment request has been submitted',
                                         'enrollment': 'true',
                                         'enrollment_status': 0
                                         },
                                        status.HTTP_200_OK,
                                        content_type='application/json')
                # offline paid
                elif skill_offering_info.offering_type == 0 and skill_offering_info.offering_kind == 1:
                    try:
                        check_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                            student_id=student_info.student_id,
                            skill_offering_id=skill_offering_info.id)
                        return Response({'message': 'You have already enrolled to this course', 'enrollment': 'false'},
                                        status.HTTP_200_OK,
                                        content_type='application/json')
                    except SKillOfferingEnrollment.DoesNotExist:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                            student_id=student_info.student_id,
                            college_id=student_info.student.college_id,
                            knowledge_partner_id=skill_offering_info.knowledge_partner.id,
                            skill_offering_id=skill_offering_info.id,
                            status=0,
                            offering_type=skill_offering_info.offering_type)  # approved / active status
                        new_skill_offering_enrollment.save()
                        return Response({'message': 'Course enrollment request has been submitted',
                                         'enrollment': 'true',
                                         'enrollment_status': 0
                                         },
                                        status.HTTP_200_OK,
                                        content_type='application/json')
                else:
                    try:
                        check_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                            student_id=student_info.student_id,
                            skill_offering_id=skill_offering_info.id)
                        return Response({'message': 'You have already enrolled in this course'}, status.HTTP_200_OK,
                                        content_type='application/json')
                    except SKillOfferingEnrollment.DoesNotExist:
                        new_skill_offering_enrollment = SKillOfferingEnrollment.objects.create(
                            student_id=student_info.student_id,
                            college_id=student_info.student.college_id,
                            knowledge_partner_id=skill_offering_info.knowledge_partner.id,
                            skill_offering_id=skill_offering_info.id,
                            status=0,
                            offering_type=skill_offering_info.offering_type)
                        new_skill_offering_enrollment.save()
                        return Response({'message': 'Course enrollment request has been submitted',
                                         'enrollment': 'true'},
                                        status.HTTP_200_OK,
                                        content_type='application/json')

            except SKillOffering.DoesNotExist:
                return Response({'message': 'skill_offering_id is Invalid', 'enrollment': 'false'}, status.HTTP_200_OK,
                                content_type='application/json')
    elif request.method == 'GET':
        student_info = UserDetail.objects.get(user_id=request.user.id)
        skill_offering_id = request.GET.get('skill_offering_id', None)
        if skill_offering_id is None:
            return Response({'message': 'skill_offering_id is Invalid'}, status.HTTP_200_OK,
                            content_type='application/json')
        try:
            get_skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                student_id=student_info.student_id,
                skill_offering_id=skill_offering_id)
            return Response({
                'enrollment_id': get_skill_offering_enrollment.id,
                'student_id': get_skill_offering_enrollment.student_id,
                'student_name': (
                        get_skill_offering_enrollment.student.first_name + ' ' + get_skill_offering_enrollment.student.last_name) if get_skill_offering_enrollment.student.first_name else '',
                'college_id': get_skill_offering_enrollment.college_id,
                'college_name': get_skill_offering_enrollment.college.college_name,
                'knowledge_partner': {
                    'id': get_skill_offering_enrollment.knowledge_partner_id,
                    'name': get_skill_offering_enrollment.knowledge_partner.name if get_skill_offering_enrollment.knowledge_partner_id else None,
                    'description': get_skill_offering_enrollment.knowledge_partner.description,
                    'website': get_skill_offering_enrollment.knowledge_partner.website,
                    'logo': get_skill_offering_enrollment.knowledge_partner.logo.url if get_skill_offering_enrollment.knowledge_partner.logo else None
                },
                'skill_offering_id': get_skill_offering_enrollment.skill_offering.id,
                'technology': get_skill_offering_enrollment.skill_offering.technology.name if get_skill_offering_enrollment.skill_offering.technology_id else None,
                'course_name': get_skill_offering_enrollment.skill_offering.course_name,
                'year_of_study': get_skill_offering_enrollment.skill_offering.year_of_study.values('year'),
                'mode_of_delivery': get_skill_offering_enrollment.skill_offering.mode_of_delivery,
                'duration': get_skill_offering_enrollment.skill_offering.duration,
                'certification': get_skill_offering_enrollment.skill_offering.certification,
                'offering_kind': get_skill_offering_enrollment.skill_offering.offering_kind,
                'link': get_skill_offering_enrollment.skill_offering.link,
                'cost': get_skill_offering_enrollment.skill_offering.cost,
                'created': get_skill_offering_enrollment.created,
                'updated': get_skill_offering_enrollment.updated,
                'comment': get_skill_offering_enrollment.comment,
                'offering_type': get_skill_offering_enrollment.skill_offering.offering_type if get_skill_offering_enrollment.skill_offering_id else None,
                'status': get_skill_offering_enrollment.status,
                'lms_course_id': get_skill_offering_enrollment.lms_course_id,
                'is_lms': False if get_skill_offering_enrollment.skill_offering.lms_course is None else True,
                'lms_id': None if get_skill_offering_enrollment.skill_offering.lms_course is None else get_skill_offering_enrollment.skill_offering.lms_course.id,

            }, status.HTTP_200_OK,
                content_type='application/json')
        except SKillOfferingEnrollment.DoesNotExist:
            return Response({'message': 'You have not enrolled to this course',
                             'status': False,
                             'is_lms': False,
                             }, status.HTTP_200_OK, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def skill_offering_enrollment_update(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    skill_offering_enrollment_id = request.POST.get('skill_offering_enrollment_id', None)
    if skill_offering_enrollment_id is None:
        return Response({'message': 'skill_offering_enrollment_id is Invalid'}, status.HTTP_200_OK,
                        content_type='application/json')
    if account_role == AccountRole.KNOWLEDGE_PARTNER:
        knowledge_partner = KnowledgePartner.objects.get(user_id=request.user.id)
        try:
            skill_offering_enrollment_info = SKillOfferingEnrollment.objects.get(
                id=skill_offering_enrollment_id,
                knowledge_partner_id=knowledge_partner.id,
            )
            enrollment_status = request.POST.get('enrollment_status', None)
            enrollment_comment = request.POST.get('enrollment_comment', None)
            skill_offering_enrollment_info.status = skill_offering_enrollment_info.status if enrollment_status is None else enrollment_status if enrollment_status in [
                '4', '3'] else skill_offering_enrollment_info.status
            skill_offering_enrollment_info.comment = skill_offering_enrollment_info.comment if enrollment_comment is None else enrollment_comment
            skill_offering_enrollment_info.save()
            return Response({'message': 'Course enrollment request has been submitted',
                             'data': {
                                 'enrollment_id': skill_offering_enrollment_info.id,
                                 'student_id': skill_offering_enrollment_info.student_id,
                                 'student_name': skill_offering_enrollment_info.student.first_name + ' ' + skill_offering_enrollment_info.student.last_name if skill_offering_enrollment_info.student.first_name else '',
                                 'college_id': skill_offering_enrollment_info.college_id,
                                 'college_name': skill_offering_enrollment_info.college.college_name,
                                 'knowledge_partner_id': skill_offering_enrollment_info.knowledge_partner_id,
                                 'knowledge_partner_name': skill_offering_enrollment_info.knowledge_partner.name,
                                 'skill_offering_id': skill_offering_enrollment_info.skill_offering_id,
                                 'skill_offering_name': skill_offering_enrollment_info.skill_offering.course_name,
                                 'status': skill_offering_enrollment_info.status,
                                 'comment': skill_offering_enrollment_info.comment,
                                 'offering_type': skill_offering_enrollment_info.skill_offering.offering_type if skill_offering_enrollment_info.skill_offering_id else None,
                                 'created': skill_offering_enrollment_info.created,
                                 'updated': skill_offering_enrollment_info.updated,

                             }},
                            status.HTTP_200_OK,
                            content_type='application/json')
        except SKillOffering.DoesNotExist:
            return Response({'message': 'skill_offering_id is Invalid', 'enrollment': 'false'}, status.HTTP_200_OK,
                            content_type='application/json')
    elif account_role == AccountRole.COLLEGE_ADMIN or account_role == AccountRole.COLLEGE_ADMIN_STAFF:
        college_info = UserDetail.objects.select_related('college').get(user_id=request.user.id)
        try:
            skill_offering_enrollment_info = SKillOfferingEnrollment.objects.get(
                id=skill_offering_enrollment_id,
                college_id=college_info.college_id,
            )
            enrollment_status = request.POST.get('enrollment_status', None)
            enrollment_comment = request.POST.get('enrollment_comment', None)
            skill_offering_enrollment_info.status = skill_offering_enrollment_info.status if enrollment_status is None else enrollment_status if enrollment_status in [
                '1', '2'] else skill_offering_enrollment_info.status
            skill_offering_enrollment_info.comment = skill_offering_enrollment_info.comment if enrollment_comment is None else enrollment_comment
            skill_offering_enrollment_info.save()
            return Response({'message': 'Course enrollment request has been submitted',
                             'data': {
                                 'enrollment_id': skill_offering_enrollment_info.id,
                                 'student_id': skill_offering_enrollment_info.student_id,
                                 'student_name': skill_offering_enrollment_info.student.first_name + ' ' + skill_offering_enrollment_info.student.last_name if skill_offering_enrollment_info.student.first_name else '',
                                 'college_id': skill_offering_enrollment_info.college_id,
                                 'college_name': skill_offering_enrollment_info.college.college_name,
                                 'knowledge_partner_id': skill_offering_enrollment_info.knowledge_partner_id,
                                 'knowledge_partner_name': skill_offering_enrollment_info.knowledge_partner.name,
                                 'skill_offering_id': skill_offering_enrollment_info.skill_offering_id,
                                 'skill_offering_name': skill_offering_enrollment_info.skill_offering.course_name,
                                 'status': skill_offering_enrollment_info.status,
                                 'comment': skill_offering_enrollment_info.comment,
                                 'offering_type': skill_offering_enrollment_info.skill_offering.offering_type if skill_offering_enrollment_info.skill_offering_id else None,
                                 'created': skill_offering_enrollment_info.created,
                                 'updated': skill_offering_enrollment_info.updated,

                             }},
                            status.HTTP_200_OK,
                            content_type='application/json')
        except SKillOffering.DoesNotExist:
            return Response({'message': 'skill_offering_id is Invalid', 'enrollment': 'false'}, status.HTTP_200_OK,
                            content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def skill_offering_enrollment_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    is_mandatory = request.GET.get('is_mandatory', None)
    query = {}
    if is_mandatory is not None and is_mandatory == 'true':
        query['is_mandatory'] = 1
    elif is_mandatory == 'false':
        query['is_mandatory'] = 0
    else:
        query['is_mandatory'] = 0

    if account_role == AccountRole.STUDENT:
        student_info = UserDetail.objects.select_related('student', 'student__college').get(user_id=request.user.id)
        query['student_id'] = student_info.student_id
    elif account_role == AccountRole.COLLEGE_ADMIN or account_role == AccountRole.COLLEGE_ADMIN_STAFF:
        college_info = UserDetail.objects.select_related('college').get(user_id=request.user.id)
        query['college_id'] = college_info.college_id
    elif account_role == AccountRole.KNOWLEDGE_PARTNER:
        knowledge_partner = KnowledgePartner.objects.get(user_id=request.user.id)
        query['knowledge_partner_id'] = knowledge_partner.id
    return Response([{
        'enrollment_id': x.id,
        'student_id': x.student_id,
        'student_name': (
                str(x.student.first_name) + ' ' + str(x.student.last_name)) if x.student.first_name is not None else None,
        'college_id': x.college_id,
        'college_name': x.college.college_name,
        'knowledge_partner': {
            'id': x.knowledge_partner_id,
            'name': x.knowledge_partner.name,
            'description': x.knowledge_partner.description,
            'website': x.knowledge_partner.website,
            'logo': x.knowledge_partner.logo.url if x.knowledge_partner.logo else None
        },
        'skill_offering_id': x.skill_offering_id,
        'technology': (x.skill_offering.technology.name if x.skill_offering.technology_id else None) if x.skill_offering_id else None,
        'course_name': x.skill_offering.course_name if x.skill_offering_id else None,
        'year_of_study': x.skill_offering.year_of_study.values('year') if x.skill_offering_id else None,
        'mode_of_delivery': x.skill_offering.mode_of_delivery if x.skill_offering_id else None,
        'duration': x.skill_offering.duration if x.skill_offering_id else None,
        'certification': x.skill_offering.certification if x.skill_offering_id else None,
        'offering_kind': x.skill_offering.offering_kind if x.skill_offering_id else None,
        'link': x.skill_offering.link if x.skill_offering_id else None,
        'cost': x.skill_offering.cost if x.skill_offering_id else None,
        'created': x.created,
        'updated': x.updated,
        'comment': x.comment,
        'offering_type': x.skill_offering.offering_type if x.skill_offering_id else None,
        'status': x.status,
        'lms_course_id': x.skill_offering.lms_course_id if x.skill_offering_id else None,
        'is_lms': (False if x.skill_offering.lms_course is None else True) if x.skill_offering_id else False,
        'lms_id': (None if x.skill_offering.lms_course is None else x.skill_offering.lms_course.id) if x.skill_offering_id else None,

    } for x in SKillOfferingEnrollment.objects.filter(**query).order_by('-id')], status.HTTP_200_OK,
        content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def skill_offering_enrollment_progress(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    skill_offering_enrollment_id = request.POST.get('skill_offering_enrollment_id', None)
    query = {}
    if skill_offering_enrollment_id is None:
        return Response({'message': 'skill_offering_enrollment_id is Invalid'}, status.HTTP_200_OK,
                        content_type='application/json')
    course_details_dir = None
    if account_role == AccountRole.KNOWLEDGE_PARTNER:
        knowledge_partner = KnowledgePartner.objects.get(user_id=request.user.id)
        try:
            skill_offering_enrollment_info = SKillOfferingEnrollment.objects.get(
                id=skill_offering_enrollment_id,
                knowledge_partner_id=knowledge_partner.id,
            )
            if skill_offering_enrollment_info.skill_offering_id:
                course_details_dir = {
                    'course_name': skill_offering_enrollment_info.skill_offering.course_name,
                    'knowledge_partner_id': knowledge_partner.id,
                    'knowledge_partner_name': knowledge_partner.name,
                    'website': knowledge_partner.website,
                    'logo': knowledge_partner.logo.url if knowledge_partner.logo else None,
                }
            try:
                enrollment_progress = SKillOfferingEnrollmentProgress.objects.get(
                    skill_offering_enrollment_id=skill_offering_enrollment_info.id,
                    knowledge_partner_id=knowledge_partner.id,
                )
                progress_percentage = request.POST.get('progress_percentage', None)
                assessment_status = request.POST.get('assessment_status', None)
                course_complete = request.POST.get('course_complete', None)
                certificate_issued = request.POST.get('certificate_issued', None)
                enrollment_progress.progress_percentage = progress_percentage if progress_percentage is not None else enrollment_progress.progress_percentage
                enrollment_progress.assessment_status = enrollment_progress.assessment_status if assessment_status is None else True if assessment_status == 'true' else False if assessment_status == 'false' else enrollment_progress.assessment_status
                enrollment_progress.course_complete = enrollment_progress.course_complete if course_complete is None else True if course_complete == 'true' else False if course_complete == 'false' else enrollment_progress.course_complete
                enrollment_progress.certificate_issued = enrollment_progress.certificate_issued if certificate_issued is None else True if certificate_issued == 'true' else False if certificate_issued == 'false' else enrollment_progress.certificate_issued
                enrollment_progress.save()


                data = {
                    'progress_percentage': round(enrollment_progress.progress_percentage, 2) if enrollment_progress.progress_percentage else 0,
                    'assessment_status': enrollment_progress.assessment_status,
                    'course_complete': enrollment_progress.course_complete,
                    'certificate_issued': enrollment_progress.certificate_issued,
                    'assessment_data': enrollment_progress.assessment_data,
                    'feedback_status': enrollment_progress.feedback_status,
                    'course_and_kp_details': course_details_dir
                }
                return Response(
                    {'message': 'Skill Offering Enrollment Progress Updated Successfully', 'data': data},
                    status.HTTP_200_OK,
                    content_type='application/json')
            except SKillOfferingEnrollmentProgress.DoesNotExist:
                enrollment_progress = SKillOfferingEnrollmentProgress.objects.create(
                    skill_offering_enrollment_id=skill_offering_enrollment_info.id,
                    knowledge_partner_id=knowledge_partner.id,
                )
                progress_percentage = request.POST.get('progress_percentage', None)
                assessment_status = request.POST.get('assessment_status', None)
                course_complete = request.POST.get('course_complete', None)
                certificate_issued = request.POST.get('certificate_issued', None)
                enrollment_progress.progress_percentage = progress_percentage if progress_percentage is not None else enrollment_progress.progress_percentage
                enrollment_progress.assessment_status = enrollment_progress.assessment_status if assessment_status is None else True if assessment_status == 'true' else False if assessment_status == 'false' else enrollment_progress.assessment_status
                enrollment_progress.course_complete = enrollment_progress.course_complete if course_complete is None else True if course_complete == 'true' else False if course_complete == 'false' else enrollment_progress.course_complete
                enrollment_progress.certificate_issued = enrollment_progress.certificate_issued if certificate_issued is None else True if certificate_issued == 'true' else False if certificate_issued == 'false' else enrollment_progress.certificate_issued
                enrollment_progress.save()
                data = {
                    'progress_percentage': round(enrollment_progress.progress_percentage, 2) if enrollment_progress.progress_percentage else 0,
                    'assessment_status': enrollment_progress.assessment_status,
                    'course_complete': enrollment_progress.course_complete,
                    'certificate_issued': enrollment_progress.certificate_issued,
                    'assessment_data': enrollment_progress.assessment_data,
                    'feedback_status': enrollment_progress.feedback_status,
                    'course_and_kp_details': course_details_dir
                }
                return Response(
                    {'message': 'Skill Offering Enrollment Progress Updated Successfully', 'data': data},
                    status.HTTP_200_OK,
                    content_type='application/json')
        except SKillOfferingEnrollment.DoesNotExist:
            return Response({'message': 'skill_offering_id is Invalid', 'enrollment': 'false'}, status.HTTP_200_OK,
                            content_type='application/json')
    elif account_role == AccountRole.STUDENT:
        student_info = UserDetail.objects.select_related('student').get(user_id=request.user.id)
        query['student_id'] = student_info.id
        print(query)
    elif account_role == AccountRole.COLLEGE_ADMIN or account_role == AccountRole.COLLEGE_ADMIN_STAFF:
        college_info = UserDetail.objects.select_related('college').get(user_id=request.user.id)
        query['college_id'] = college_info.college_id
    else:
        return Response({'message': 'not allowed', 'enrollment': 'false'}, status.HTTP_200_OK,
                        content_type='application/json')
    try:
        certificate_data = None
        skill_offering_enrollment_info = SKillOfferingEnrollment.objects.get(
            id=skill_offering_enrollment_id,
        )

        try:
            certificate_info = SKillOfferingEnrollmentCertificate.objects.get(
                skill_offering_enrollment_id=skill_offering_enrollment_info.id
            )
            certificate_data = {
                'certificate_id': certificate_info.certificate_id if certificate_info.certificate else None,
                'issue_at': certificate_info.issue_at,
                'certificate_no': certificate_info.certificate_no,
            }
        except:
            pass

        if skill_offering_enrollment_info.skill_offering_id:
            knowledge_partner = skill_offering_enrollment_info.skill_offering.knowledge_partner
            course_details_dir = {
                'course_name': skill_offering_enrollment_info.skill_offering.course_name,
                'knowledge_partner_id': knowledge_partner.id if knowledge_partner else None,
                'knowledge_partner_name': knowledge_partner.name if knowledge_partner else None,
                'website': knowledge_partner.website if knowledge_partner else None,
                'logo': (knowledge_partner.logo.url if knowledge_partner.logo else None) if knowledge_partner else None,
            }
        try:
            enrollment_progress = SKillOfferingEnrollmentProgress.objects.get(
                skill_offering_enrollment_id=skill_offering_enrollment_info.id,
            )
            data = {
                'progress_percentage': round(enrollment_progress.progress_percentage, 2) if enrollment_progress.progress_percentage else 0,
                'assessment_status': enrollment_progress.assessment_status,
                'course_complete': enrollment_progress.course_complete,
                'certificate_issued': enrollment_progress.certificate_issued,
                'assessment_data': enrollment_progress.assessment_data,
                'feedback_status': enrollment_progress.feedback_status,
                'course_and_kp_details': course_details_dir,
                'certificate_data': certificate_data
            }
            return Response(
                {'message': 'Skill Offering Enrollment Progress', 'data': data},
                status.HTTP_200_OK,
                content_type='application/json')
        except SKillOfferingEnrollmentProgress.DoesNotExist:
            new_enrollment_progress = SKillOfferingEnrollmentProgress(
                skill_offering_enrollment_id=skill_offering_enrollment_info.id,
            )
            new_enrollment_progress.save()
            data = {
                'progress_percentage': round(new_enrollment_progress.progress_percentage, 2) if enrollment_progress.progress_percentage else 0,
                'assessment_status': new_enrollment_progress.assessment_status,
                'course_complete': new_enrollment_progress.course_complete,
                'certificate_issued': new_enrollment_progress.certificate_issued,
                'assessment_data': new_enrollment_progress.assessment_data,
                'feedback_status': new_enrollment_progress.feedback_status,
                'course_and_kp_details': course_details_dir,
                'certificate_data': certificate_data
            }
            return Response(
                {'message': 'Skill Offering Enrollment Progress', 'data': data},
                status.HTTP_200_OK,
                content_type='application/json')
    except SKillOfferingEnrollment.DoesNotExist:
        return Response({'message': 'skill_offering_id is Invalid', 'enrollment': 'false'}, status.HTTP_200_OK,
                        content_type='application/json')
