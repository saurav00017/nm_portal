# from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
import math
from .models import SimpleCourse as SC


# @cache_page(60 * 15)
@api_view(['GET'])
def simple_courses_list(request):
    categories = SC.objects.all().distinct('category')
    final = []
    for category in categories:
        temp = {
            'category': category.category,
        }
        temp_category_courses = SC.objects.filter(category=category.category)
        course_l = []
        for course in temp_category_courses:
            course_l.append({
                'name': course.name,
                'course_type': course.course_type,
                'lms_id': course.lms_course_id if course.lms_course is not None else None,
                'link': course.link,
                'hours': course.hours,
                'partner_details': {
                    'name': course.knowledge_partner.name,
                    'link': course.knowledge_partner.website,
                    'logo': course.knowledge_partner.logo.url if course.knowledge_partner.logo else None,
                }
            })
        temp['courses'] = course_l
        final.append(temp)
    return Response(final, status=status.HTTP_200_OK)
