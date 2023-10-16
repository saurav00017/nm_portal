from student.models import Student
from skillofferings.models import SKillOfferingEnrollment
import os
from django.conf import settings
import csv

skill_offering_enrollment_student_ids = SKillOfferingEnrollment.objects.filter(
    is_mandatory=True,
    skill_offering__knowledge_partner_id=76
).values_list('student_id', flat=True)

student_data = Student.objects.select_related('college_id').filter(
    id__in=skill_offering_enrollment_student_ids,
).values_list(
    'aadhar_number',
    'phone_number',
    'invitation_id',
    'college__college_code',
    'college__zone__id',
    'college__zone__name',
)

headers = ['aadhar_number',
    'phone_number',
    'invitation_id',
    'college__college_code',
    'college__zone_id',
    'college__zone__name'
    ]

with open(os.path.join(settings.BASE_DIR,  'scripts/new/students/miscrosoft_data.csv'), 'w') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(list(student_data))
