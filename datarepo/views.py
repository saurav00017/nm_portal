from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from lms.models import Course
from django.shortcuts import render
from django.db.models.functions import Lower
from users.models import User
from lms.models import LMSClient
from college.models import College, CollegeStatus
from .models import (District, AffiliatedUniversity, CollegeManagementType, CollegeType, StudentCaste,
                     StudentRegistrationStatus, Gender, StudentDegree, SkillOffering, SkillOfferingFor, Branch, Zone)
from kp.models import KnowledgePartner, LinkPartner


# Create your views here.
def get_class_list(Class):
    items = Class.__dict__.items()
    items = filter(lambda key: not key[0].startswith("_"), items)
    items = dict(items)
    return {v: str(k).replace("_", " ") for k, v in sorted(items.items(), key=lambda item: item[1])}


@api_view(['GET'])
def get_districts(request):
    district_list = District.objects.values('id', 'name').all().order_by(Lower('name'))
    return Response(list(district_list), status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def get_affiliated_universities(request):
    affiliated_university_list = AffiliatedUniversity.objects.values('id', 'name').all().order_by(Lower('name'))
    return Response(list(affiliated_university_list), status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def get_college_registration_dropdowns(request):
    content = {
        'management_types': get_class_list(CollegeManagementType),
        'college_types': get_class_list(CollegeType),
    }

    return Response(content, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def get_student_registration_dropdowns(request):
    content = {
        'caste': get_class_list(StudentCaste),
        'gender': get_class_list(Gender),
        'degree': get_class_list(StudentDegree),
    }

    return Response(content, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username', None)
    if username and len(username) >= 4:

        content = {
            'status': User.objects.filter(username__iexact=username).exists()
        }
        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
    else:
        content = {
            "message": "Please provide username with minimum of 4 letters"
        }

        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
def training_partners(request):
    lms_clients = list(LMSClient.objects.values('client', 'client_logo').order_by(Lower('client')))
    lms_clients = [
        {
            'client': client['client'],
            'client_logo': "/media/" + str(client['client_logo']) if client['client_logo'] else None,
        } for client in lms_clients
    ]
    content = {
        'training_partners': list(lms_clients) if lms_clients else None
    }
    return Response(content, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def get_skill_offering_dropdowns(request):
    content = {
        'skill_offerings': get_class_list(SkillOfferingFor),
    }

    return Response(content, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def kp_list(request):
    content = [
        {
            'knowledge_partner_id': x.id,
            'name': x.name,
            'website': x.website,
            'logo': x.logo.url if x.logo else None,
        } for x in KnowledgePartner.objects.all().order_by('name')
    ]
    return Response(content, status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def get_skill_offering_list(request):
    skill_offering_for = request.GET.get('skill_offering_for', None)
    knowledge_partner_id = request.GET.get('knowledge_partner_id', None)
    query = {}
    if knowledge_partner_id:
        query['knowledge_partner_id'] = knowledge_partner_id
    if skill_offering_for:
        try:
            skill_offering_for = int(skill_offering_for)
            skill_offering_list = SkillOffering.objects.values(
                'technology',
                'training_module',
                'specialization',
                'year_of_study',
                'live_training',
                'live_virtual_training',
                'certification',
            ).filter(**query,
                     skill_offering_for=skill_offering_for).order_by(Lower('technology'))
            final_skill_offering_list = []
            last_record = None
            for skill_offer in skill_offering_list:
                technology = str(skill_offer['technology']).lower()
                certification = str(skill_offer['certification']).lower()

                if last_record != technology:
                    temp = {
                        "technology": skill_offer['technology'],
                        'items': [skill_offer]
                    }
                    final_skill_offering_list.append(temp)
                else:
                    if len(final_skill_offering_list):
                        final_skill_offering_list[len(final_skill_offering_list) - 1]['items'].append(skill_offer)
                    else:
                        final_skill_offering_list[len(final_skill_offering_list) - 1]['items'].append(skill_offer)

                last_record = technology

                #
                # if str(skill_offer['technology']).lower() in final_skill_offering_list:
                #     if certification in final_skill_offering_list[technology]:
                #         final_skill_offering_list[technology][certification].append(skill_offer)
                #     else:
                #         final_skill_offering_list[technology][certification] = [skill_offer]
                # else:
                #     final_skill_offering_list[technology] = {
                #         certification: [skill_offer]
                #     }
            content = {
                'skill_offerings_list': final_skill_offering_list,
            }
            return Response(content, status=status.HTTP_200_OK, content_type='application/json')

        except Exception as e:
            print(e)
    content = {
        'message': "Please provide valid skill offering",
    }

    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['GET'])
def get_colleges_list(request):
    list_of_colleges = College.objects.values(
        'id',
        'college_name',
        'college_code',
        'college_type',
        'management_type',
    ).filter(
        # status=CollegeStatus.PAYMENT_DONE
    ).order_by(Lower('college_name'))
    content = {
        'colleges_list': list(list_of_colleges),
    }

    return Response(content, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def branches(request):
    branch_type = request.GET.get('branch_type', None)
    query = {}
    if branch_type:
        query['branch_type'] = branch_type
    return Response([{
        'id': branch.id,
        'name': branch.name,
        'branch_type': branch.branch_type,
    } for branch in Branch.objects.filter(**query)], status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def zones(request):
    return Response([{
        'id': zone.id,
        'name': zone.name,
        'district_name': zone.district.name if zone.district_id else None,
    } for zone in Zone.objects.all()], status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET'])
def link_partner_list(request):
    content = [
        {
            'link_partner_id': x.id,
            'name': x.name,
            'description': x.description,
            'website': x.website,
            'logo': x.logo.url if x.logo else None,
        } for x in LinkPartner.objects.all().order_by(Lower('name'))
    ]
    return Response(content, status.HTTP_200_OK, content_type='application/json')

#
# @api_view(['GET'])
# def academic_partners(request):
#     college_name = request.GET.get('college_name', None)
#     college_type = request.GET.get('college_type', None)
#     management_type = request.GET.get('management_type', None)
#     query = {}
#     if college_type:
#         try:
#             college_type = int(college_type)
#             query['college_type'] = college_type
#         except:
#             pass
#     if management_type:
#         try:
#             management_type = int(management_type)
#             query['management_type'] = management_type
#         except:
#             pass
#     colleges_list = list(
#         College.objects.filter(status__gte=CollegeStatus.REGISTERED)
#     )
#     content = {
#         'academic_partners': colleges_list
#     }
#     return Response(content, status=status.HTTP_200_OK, content_type='application/json')
