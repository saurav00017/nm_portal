from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Count
import csv
from io import StringIO
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail
from django.conf import settings
import requests
from django.http import HttpResponse
import requests
import json


# Create your views here.
@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def start_test(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)
    test_type = request.query_params.get('test_type', None)
    if test_type is None:
        return Response({"error": "test_type is required"}, status=status.HTTP_400_BAD_REQUEST)
    query = {}
    if account_role == AccountRole.STUDENT and test_type == '1':
        # get student details
        student_info = UserDetail.objects.select_related('student').get(user_id=request.user.id)
        url = "https://naanmudhalvan.mean-median-mode.com/NMApi/nm_candidate_data_post1"

        payload = {'apikey': 'a4c469cda0d35b529a05947e5c52123a',
                   'cc_key': 'MTYwOTIwMTIwMTI1NTVhNGM0NjljZGEwZDM1YjUyOWEwNTk0N2U1YzUyMTIzYQ==',
                   'candidate_unique_id': student_info.student.invitation_id,
                   'email_id': student_info.student.email,
                   'mobile': student_info.student.phone_number,
                   'edu_type': '3',
                   'education': '4',
                   'spec': '4',
                   'time_stamp': '16092012012555',
                   'name': str(student_info.student.aadhar_number),
                   'return_link': 'https://portal.naanmudhalvan.tn.gov.in/students/psychometric'}
        files = [

        ]
        headers = {
            'Cookie': 'ci_session=j2he8lv7t92588q1601n8kb3btmtsuf8'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        json = response.json()
        if json['status'] and json['result_code'] in ['100', '101', '400']:
            content = {
                'message': 'HTML',
                'response': {
                    'test_url': json['result_link'],
                }
            }
            return Response(content, status=status.HTTP_200_OK, content_type='application/json')
        else:
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    elif account_role == AccountRole.STUDENT and test_type == '2':
        # get student details
        student_info = UserDetail.objects.select_related('student').get(user_id=request.user.id)
        url = "https://api.hiremee.co.in/api/v11/psychometric-test-token"
        import json
        payload = json.dumps({
        "client_key": "384qly2id5gr61b",
        "client_secret": "xipfj3v4d0e7rth"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        try:

            response_data = json.loads(response.content)
        except:
            content = {
                'message': 'Please try again',
                "error": str(response.content)
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        if 'access_key' not in response_data:
            content = {
                'message': 'Please try again'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

        access_key = response_data['access_key']

        # second call
        url2 = "https://api.hiremee.co.in/api/v12/test-initiate"

        payload = json.dumps({
            "full_name": str(student_info.student.aadhar_number),
            "email_address": str(student_info.student.email),
            "mobile_number": 9999999999,
            "user_unqiue_id": str(student_info.student.invitation_id),
            'college_name': str(student_info.student.college.college_name) if student_info.student.college_id else '',
            'college_code': str(student_info.student.college.college_code) if student_info.student.college_id else '',
            'year_of_passing': str(student_info.student.year_of_study) if student_info.student.year_of_study else '',
            'specialization_id': student_info.student.rbranch_id,
        })
        headers = {
            'Authorization': 'Bearer ' + access_key,
            'Content-Type': 'application/json'
        }

        response_second = requests.request("POST", url2, headers=headers, data=payload)
        try:
            content = {
                'message': 'HTML',
                'response': response_second.json()
            }

            return Response(content, content_type='application/json', status=status.HTTP_200_OK, )
        except:
            content = {
                'message': 'Please try again',
                'error': str(response_second.content)
            }

            return Response(content, content_type='application/json', status=status.HTTP_200_OK, )
    else:
        content = {
            'message': 'invalid'
        }
        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
