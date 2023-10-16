from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from lms.models import Course
from django.shortcuts import render
from django.db.models.functions import Lower
from users.models import User
from lms.models import LMSClient
from ..models import Announcement
import requests

@api_view(['GET'])
def announcements_list(request):
    return Response([
        {
            "date": announcement.date,
            "link": announcement.link,
            "title": announcement.title,
            "description": announcement.description,
            "title_tamil": announcement.title_tamil,
            "description_tamil": announcement.description_tamil,
        } for announcement in Announcement.objects.all().order_by('-created')
    ], status=status.HTTP_200_OK)


@api_view(['POST'])
def announcements_update(request):
    url = "https://api.npoint.io/ed3ac76d12eec896fca9"
    response = requests.get(url)
    try:
        records = response.json()

        for data in records:

            _date = data['date'] if 'date' in data else None
            link = data['link'] if 'link' in data else None
            title = data['title'] if 'title' in data else None
            description = data['description'] if 'description' in data else None
            title_tamil = data['title_tamil'] if 'title_tamil' in data else None
            description_tamil = data['description_tamil'] if 'description_tamil' in data else None
            try:
                announcement = Announcement.objects.get(
                    title=title
                )
                announcement.link = link
                announcement.description = description
                announcement.title_tamil = title_tamil
                announcement.description_tamil = description_tamil
                announcement.date = _date
                announcement.save()
            except Announcement.DoesNotExist:
                announcement = Announcement.objects.create(
                    title=title,
                    description=description,
                    link=link,
                    title_tamil=title_tamil,
                    description_tamil=description_tamil,
                    date=_date,
                )
        return Response({"message": "updated successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)