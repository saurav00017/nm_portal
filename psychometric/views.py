from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cerberus import Validator
import yaml
from datarepo.models import AccountRole
import json
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import PsychometricPartner, PsychometricResult
from json.decoder import JSONDecodeError
from student.models import Student


@api_view(['POST'])
def psychometric_token(request):
    try:
        json_data = json.loads(request.body)
        client_key = json_data.get('client_key', None)
        client_secret = json_data.get('client_secret', None)
        request_schema = '''
            client_key:
                type: string
                empty: false
                required: true
                minlength: 5
            client_secret:
                type: string
                empty: false
                min: 6
                required: true
                minlength: 6
            '''
        v = Validator()
        post_data = json_data
        schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
        if v.validate(post_data, schema):
            try:
                psychometric_user = PsychometricPartner.objects.get(
                    client_key=client_key,
                    client_secret=client_secret,
                    status=True
                )
                if psychometric_user.client.account_role == AccountRole.PSYCHOMETRIC_API_USER:
                    refresh_token = TokenObtainPairSerializer.get_token(user=psychometric_user.client)
                    content = {
                        'token': str(refresh_token.access_token),
                        'refresh': str(refresh_token),
                    }
                    return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                else:
                    content = {
                        'message': "Please provide valid client key/ secret in headers",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST,
                                    content_type='application/json')
            except PsychometricPartner.DoesNotExist:
                content = {
                    'message': "Invalid credentials",
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        else:
            content = {
                'message': "invalid request",
                'errors': v.errors
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def psychometric_refresh(request):
    try:

        json_data = json.loads(request.body)
        refresh = json_data.get('refresh', None)
        request_schema = '''
            refresh:
                type: string
                empty: false
                required: true
            '''
        v = Validator()
        post_data = json_data
        schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
        if v.validate(post_data, schema):
            try:

                refresh = RefreshToken(refresh)
                content = {
                    'token': str(refresh.access_token),
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

            except TokenError:
                content = {
                    'message': 'Token is invalid or expired',
                }
                return Response(content, status=status.HTTP_200_OK, content_type='application/json')

        else:
            content = {
                'message': "invalid request",
                'errors': v.errors
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
    except json.decoder.JSONDecodeError:
        content = {
            'message': "Please provide valid json data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def psychometric_results(request):
    try:
        json_data = json.loads(request.body)
        student_id = json_data.get('user_unique_id', None)
        result_data = json_data.get('data', None)
        report_url = json_data.get('report_url', None)
        try:
            partner_details = PsychometricPartner.objects.get(client_id=request.user.id)
            if partner_details.client.account_role == AccountRole.PSYCHOMETRIC_API_USER:
                try:
                    student_details = Student.objects.get(invitation_id=student_id)
                    try:
                        psychometric_result = PsychometricResult.objects.get(student_id=student_details.id)
                        psychometric_result.result = result_data
                        psychometric_result.report_url = report_url
                        psychometric_result.save()
                        content = {
                            'message': "Results have been updated",
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                    except PsychometricResult.DoesNotExist:
                        psychometric_result = PsychometricResult.objects.create(
                            student_id=student_details.id,
                            client_id=partner_details.id,
                            college_id=student_details.college_id,
                            result=result_data
                        )
                        psychometric_result.save()
                        content = {
                            'message': "Results have been submitted",
                        }
                        return Response(content, status=status.HTTP_200_OK, content_type='application/json')
                except Student.DoesNotExist:
                    content = {
                        'message': "Invalid user_unique_id",
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "You dont have the permission",
                }
                return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
        except PsychometricPartner.DoesNotExist:
            content = {
                'message': "You dont have the permission",
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    except JSONDecodeError:
        content = {
            'message': "Invalid data",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
