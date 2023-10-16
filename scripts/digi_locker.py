from dict2xml import dict2xml
from datetime import datetime
"""
certificate_no
student_name
roll_no
Branch
college_name
course_name
partner_name
date_of_issue

"""
data = {
    'DocDetails': {
        'DocType': "PDF",
        "DigiLockerId": "locker",
        "UID": "234sdfwfwef",
        "FullName": "Chandu",
        "DOB": "",
        "Photo": "",
        "StudentName": "Chandu",
        "CertificateNo": "NME23432213",
        "RollNo": "123123123",
        "Branch": "CSC",
        "CollegeName": "College name",
        "CourseName": "Python Programming",
        "PartnerName": "Veranda",
        "DateOfIssue": "12/12/2022",
    }
}
docType = 'PDF'
digiLockerId = ''
fullName = ''
studentName = ''
certificateNo = ''
rollNo = ''
branch = ''
collegeName = ''
courseName = ''
partnerName = ''
dateOfIssue = ''
ts = str(datetime.now())
payload = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?> <PullURIRequest xmlns:ns2="http://tempuri.org/" ver="1.0" ts="{ts}" txn="1234" orgId="" format="xml/pdf/both"> <DocDetails>
<DocType>{docType}</DocType> //Document type
<DigiLockerId>{digiLockerId}</DigiLockerId > //Unique 36 character DigiLocker Id <UID></UID> //Aadhaar number (Optional)
<FullName>{fullName}</FullName> //Name as on Aadhaar (Optional)
<DOB></DOB> //Date of birth as on Aadhaar (Optional) <Photo></Photo> //Base 64 encoded JPEG photograph as on Aadhaar
(Optional)
    <StudentName>{studentName}</StudentName> //User defined field
    <CertificateNo>{certificateNo}</CertificateNo> //User defined field
    <RollNo>{rollNo}</RollNo> //User defined field
    <Branch>{branch}</Branch> //User defined field
    <CollegeName>{collegeName}</CollegeName> //User defined field
    <CourseName>{courseName}</CourseName> //User defined field
    <PartnerName>{partnerName}</PartnerName> //User defined field
    <DateOfIssue>{dateOfIssue}</DateOfIssue> //User defined field
</DocDetails>
</PullURIRequest>"""

xml = dict2xml(data)
print(xml)

