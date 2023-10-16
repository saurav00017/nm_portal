from django.shortcuts import HttpResponse
from django.http import FileResponse, Http404
from dicttoxml import dicttoxml
from django.views.decorators.csrf import csrf_exempt
import xmltodict
import json
from skillofferings.models import SKillOfferingEnrollmentCertificate
from django.conf import settings

@csrf_exempt
def digi_locker_pull_certificate(request):
    text = request.body
    d = json.dumps(xmltodict.parse(text, xml_attribs=False), indent=4)
    print(d)
    payload_data = json.loads(d)['PullURIRequest']['DocDetails']
    docType = payload_data.get('DocType', None)
    studentName = payload_data.get('StudentName', None)
    certificateNo = payload_data.get('certificateNo', None)
    rollNo = payload_data.get('RollNo', None)
    branch = payload_data.get('Branch', None)
    collegeName = payload_data.get('CollegeName', None)
    courseName = payload_data.get('CourseName', None)
    partnerName = payload_data.get('PartnerName', None)
    dateOfIssue = payload_data.get('DateOfIssue', None)
    query = {}
    if certificateNo:
        query['certificate_no__iexact'] = certificateNo

    if studentName:
        query['skill_offering_enrollment__student__aadhar_number__iexact'] = studentName
    if rollNo:
        query['skill_offering_enrollment__student__roll_no__iexact'] = rollNo
    if branch:
        query['skill_offering_enrollment__student__rbranch__name__iexact'] = branch
    if collegeName:
        query['skill_offering_enrollment__student__college__college_name__iexact'] = collegeName
    if courseName:
        query['skill_offering_enrollment__skill_offering__course_name__iexact'] = courseName
    if partnerName:
        query['skill_offering_enrollment__skill_offering__knowledge_partner__name__iexact'] = partnerName
    if dateOfIssue:
        query['data__icontains'] = dateOfIssue
    print(query)
    record = SKillOfferingEnrollmentCertificate.objects.filter(certificate__isnull=False, **query).order_by('-id').first()
    if record:
        if str(docType).lower() == 'pdf':
            print(record.certificate.url)

            img = open(f"{settings.BASE_DIR}/{record.certificate.url}", 'rb')
            return FileResponse(img)
        elif str(docType).lower() in 'xml':
            student = record.skill_offering_enrollment.student
            skill_offering = record.skill_offering_enrollment.skill_offering
            content = {'DocDetails': {
                "DocType": docType,
                "UID": "",
                "DOB": "",
                "Photo": "",
                **record.data,
            }}
            return HttpResponse(dicttoxml(content, custom_root='PullURIRequest'))
    else:
        raise Http404("Certificate not found")


@csrf_exempt
def digi_locker_push(request):
    text = request.body
    d = json.dumps(xmltodict.parse(text, xml_attribs=False), indent=4)
    print(d)
    content = {'DocDetails': {
        "DocType": "DocType",
        "DigiLockerId": "DocType",
        "UID": "DocType",
        "FullName": "DocType",
        "DOB": "DocType",
        "Photo": "DocType",
        'StudentName': ""
    }}
    return HttpResponse(dicttoxml(content, custom_root='PullURIRequest'))

