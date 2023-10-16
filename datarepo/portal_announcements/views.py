from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from lms.models import Course
from django.shortcuts import render
from django.db.models.functions import Lower
from users.models import User, UserDetail
from lms.models import LMSClient
from ..models import PortalAnnouncement, AccountRole
import requests
import jwt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.db.models import Q

@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def portal_announcements_list(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    page = request.GET.get('page', 0)
    limit = request.GET.get('limit', 20)
    view_all = request.GET.get('view_all', None)
    college_type = request.GET.get('college_type', None)
    announcement_type = request.GET.get('announcement_type', None)
    try:
        page = int(page)
        limit = int(limit)
    except:
        page = 0
        limit = 20

    query = {}
    if college_type:
        query['college_type'] = college_type
    if announcement_type:
        query['announcement_type'] = announcement_type
    q_query = None
    total_count = PortalAnnouncement.objects.filter(**query).count()
    if view_all:
        limit = total_count
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        pass
    elif account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        user_details = UserDetail.objects.select_related('college').get(user_id=request.user.id)
        query['announcement_type__in'] = [0, 1]
        q_query = Q(Q(college_type=None) | Q(college_type=user_details.college.college_type))
        # query['college_type__in'] = [None, user_details.college.college_type]
    elif account_role == AccountRole.STUDENT:
        user_details = UserDetail.objects.select_related('student', 'student__college').get(user_id=request.user.id)
        query['announcement_type__in'] = [0, 2]
        q_query = Q(Q(college_type=None) | Q(college_type=user_details.student.college.college_type))
        # query['college_type__in'] = [None, user_details.student.college.college_type]
        pass
    else:
        return Response({"message": "You dont have the permission"}, status=status.HTTP_400_BAD_REQUEST)
    if q_query:
        announcements = PortalAnnouncement.objects.filter(q_query, **query).order_by('-date')[(page * limit): ((page * limit) + limit)]
    else:
        announcements = PortalAnnouncement.objects.filter(**query).order_by('-date')[(page * limit): ((page * limit) + limit)]
    final_list = []
    for announcement in announcements:
        temp = {
            'announcement_id': announcement.id,
            "date": announcement.date,
            "link": announcement.link,
            "title": announcement.title,
            "description": announcement.description,
            "title_tamil": announcement.title_tamil,
            "description_tamil": announcement.description_tamil,
            "college_type": announcement.college_type,
            "announcement_type": announcement.announcement_type,
            "file": announcement.file.url if announcement.file else None,
        }
        final_list.append(temp)
    content = {
        "announcements": final_list,
        'filter': {
            'page': page,
            'limit': limit,
            'view_all': view_all,
            'total_count': total_count,
            'announcement_type': announcement_type,
            'college_type': college_type,
            "query": query

        }
    }
    return Response(content, status=status.HTTP_200_OK)

#
# @api_view(['POST'])
# def portal_announcement(request):
#     url = "https://api.npoint.io/ed3ac76d12eec896fca9"
#     response = requests.get(url)
#     try:
#         records = response.json()
#
#         for data in records:
#
#             _date = data['date'] if 'date' in data else None
#             link = data['link'] if 'link' in data else None
#             title = data['title'] if 'title' in data else None
#             description = data['description'] if 'description' in data else None
#             title_tamil = data['title_tamil'] if 'title_tamil' in data else None
#             description_tamil = data['description_tamil'] if 'description_tamil' in data else None
#             try:
#                 announcement = PortalAnnouncement.objects.get(
#                     title=title
#                 )
#                 announcement.link = link
#                 announcement.description = description
#                 announcement.title_tamil = title_tamil
#                 announcement.description_tamil = description_tamil
#                 announcement.date = _date
#                 announcement.save()
#             except PortalAnnouncement.DoesNotExist:
#                 announcement = PortalAnnouncement.objects.create(
#                     title=title,
#                     description=description,
#                     link=link,
#                     title_tamil=title_tamil,
#                     description_tamil=description_tamil,
#                     date=_date,
#                 )
#         return Response({"message": "updated successfully"}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)