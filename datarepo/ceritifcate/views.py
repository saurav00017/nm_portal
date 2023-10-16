from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from skillofferings.models import SKillOfferingEnrollmentCertificate
from .token import get_certificate_token, get_certificate_path_from_token
from django.http import FileResponse, Http404, HttpResponseBadRequest
import jwt
from django.conf import settings


@api_view(['POST'])
def certificate_url_token(request):
    certificate_id = request.POST.get('certificate_id', None)
    if not certificate_id:
        content = {
            'message': "Please provide certificate_id"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    try:
        record = SKillOfferingEnrollmentCertificate.objects.get(
            certificate_id=certificate_id
        )
        content = {
            'token': record.certificate_no
            #'token': get_certificate_token(record)
        }
        return Response(content, status.HTTP_200_OK, content_type='application/json')
    except SKillOfferingEnrollmentCertificate.DoesNotExist:
        content = {
            'message': "Please provide valid certificate_id"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


def certificate_image(request):
    # first = SKillOfferingEnrollmentCertificate.objects.first()
    # print(get_certificate_token(first))
    token = request.GET.get('token', None)
    if token:
        try:
            certificate_path = get_certificate_path_from_token(token)
        except jwt.exceptions.InvalidTokenError:
            return HttpResponseBadRequest("Invalid token")
        except jwt.exceptions.ExpiredSignature:
            return HttpResponseBadRequest("Token expired")
        except Exception as e:
            return HttpResponseBadRequest(f"Invalid token - {e}")
        img = open(f"{settings.BASE_DIR}/{certificate_path}", 'rb')
        response = FileResponse(img)
        return response
    raise Http404('Certificate not found')

