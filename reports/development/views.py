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

#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTTokenUserAuthentication])
# def lms_course(request):