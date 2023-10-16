
from student.models import Student, StudentPaymentDetail
import os
from rest_framework import status

from rest_framework.response import Response
import jwt
from jwt.exceptions import PyJWTError
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from users.models import User
import json
from django.conf import settings
from datarepo.models import CollegeType
RAZORPAY_USERNAME = os.environ.get('RAZORPAY_KEY', '')
RAZORPAY_SECRET_KEY = os.environ.get('RAZORPAY_SECRET_KEY', '')

CAMBRIDGE_KEY = "sghdfzgxdgfdbxfgbfgbddfbdbgiud4374eryft84evs6"


def get_nm_student_token_for_cambridge(student_id: str):
    dt = datetime.now() + timedelta(days=1)

    encoded_jwt = jwt.encode({"student_id": student_id, "exp": dt}, str(CAMBRIDGE_KEY), algorithm="HS256")
    print(encoded_jwt)
    return encoded_jwt


def get_class_list(Class):
    items = Class.__dict__.items()
    items = filter(lambda key: not key[0].startswith("_"), items)
    items = dict(items)
    return {v: str(k).replace("_", " ") for k, v in sorted(items.items(), key=lambda item: item[1])}


@api_view(['POST'])
def nm_student_details_to_cambridge(reqeust):

    try:
        student = "STUDENT_ID"
        # print("\n\nnm_student_details_to_cambridge ---->  ", get_nm_student_token_for_cambridge("TEST_USER_ID"),"\n\n")
        json_data = json.loads(reqeust.body)
        # print(json_data)
        token = json_data.get('token', None)
        if token is None:
            content = {
                'message': "Please provide token",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        # print(reqeust.POST)
        # print(token)
        payload = jwt.decode(token, str(CAMBRIDGE_KEY), algorithms=["HS256"])
        # print(payload)
        student_id: str = payload.get("student_id", None)
        if student_id is None:
            content = {
                'message': "invalid token",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        try:
            get_student = Student.objects.select_related('college').get(invitation_id=student_id)
            institution_types = get_class_list(CollegeType)
            college_type = get_student.college.college_type if get_student.college_id else None
            institution_type = None
            if college_type is not None:
                if college_type in institution_types.keys():
                    institution_type = institution_types[college_type]
            content = {
                # 'student_id': student_id,
                'studentId': student_id,
                'studentName': get_student.aadhar_number,
                'collegeCode': get_student.college.college_code if get_student.college_id else None,
                'collegeName': get_student.college.college_name if get_student.college_id else None,
                'semester': get_student.sem,
                'branch': get_student.rbranch.name if get_student.rbranch_id else None,
                'institute': institution_type,
            }
            return Response(content, status=status.HTTP_200_OK, content_type='application/json')
        except Student.DoesNotExist:
            content = {
                'message': "invalid student_id. Please contact admin",
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:
            print("nm_student_details_to_cambridge --> 1", e)
            content = {
                'message': "invalid token",
                "error": "1" +str(e)
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    except Exception as e:
        print("nm_student_details_to_cambridge --> 2", e)
        print(e)
        content = {
            'message': "invalid token",
            "error": "2" + str(e)
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


