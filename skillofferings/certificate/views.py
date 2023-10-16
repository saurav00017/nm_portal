from rest_framework import generics, status
from rest_framework.response  import Response
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress, SKillOfferingEnrollmentCertificate

@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def validate(request):
    certificate_no = request.GET.get('certificate_no', None)
    certificate = SKillOfferingEnrollmentCertificate.objects.filter(certificate_no = certificate_no).first()

    data = certificate.data

    enrollment = certificate.skill_offering_enrollment
    student_id = enrollment.student.id

    return Response({'data': data})

@api_view(['GET'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def view(request):
    certificate_no = request.GET.get('certificate_no', None)
    certificate = SKillOfferingEnrollmentCertificate.objects.filter(certificate_no = certificate_no).first()

    proxies = {
        "http": None,
        "https": None
    }

    enrollment = certificate.skill_offering_enrollment
    student_id = enrollment.student.id
    url = "http://localhost:9000/" + str(student_id) + "/?cert=" + certificate_no
    
    # retrieve the PDF file from the remote server
    response = requests.get(url, proxies=proxies)
    #print(url)
    
    # check if the response was successful
    if response.status_code == 200:
    # if so, create an HTTP response with the PDF content
        pdf_content = response.content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{certificate_no}.pdf"'
        return response
    else:
    # if the response was not successful, return an error message
        return HttpResponse(f"Failed to retrieve PDF: {response.status_code}", status=500)