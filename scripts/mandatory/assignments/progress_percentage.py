import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollmentProgress, SKillOffering, MandatoryCourse

export_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/progress_percentage_data.csv'), 'w')
writer = csv.writer(export_file)

writer.writerow(['kp_id', 'kp', 'skill_offering_id', 'course', 'ia_count', 'total_score', 'assessment_data'])
progress_list = SKillOfferingEnrollmentProgress.objects.values(
    'skill_offering_enrollment__skill_offering__knowledge_partner_id',
    'skill_offering_enrollment__skill_offering__knowledge_partner__name',
    'skill_offering_enrollment__skill_offering_id',
    'skill_offering_enrollment__skill_offering__course_name',
    'skill_offering_enrollment__skill_offering__ia_count',
    'progress_percentage',
    'assessment_data',
).filter(progress_percentage__gt=100)

for progress in progress_list:
    try:
        data = json.dumps(progress['assessment_data']) if progress['assessment_data'] else None
    except:
        try:
            data = progress['assessment_data']
        except Exception as e:
            data = None
    try:
        writer.writerow([
            progress['skill_offering_enrollment__skill_offering__knowledge_partner_id'],
            progress['skill_offering_enrollment__skill_offering__knowledge_partner__name'],
            progress['skill_offering_enrollment__skill_offering_id'],
            progress['skill_offering_enrollment__skill_offering__course_name'],
            progress['skill_offering_enrollment__skill_offering__ia_count'],
            progress['progress_percentage'],
            data
        ])
    except:
        pass