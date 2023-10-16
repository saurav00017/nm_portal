import json
import os
import csv
from django.conf import settings
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollmentProgress, SKillOffering,SKillOfferingEnrollment, MandatoryCourse

file = open(os.path.join(settings.BASE_DIR,
                         'scripts/mandatory/assignments/veranda/veranda_data.csv'), 'w')
writer = csv.writer(file)

with open(os.path.join(settings.BASE_DIR,
                       'scripts/mandatory/assignments/veranda/veranda_data_1.csv'), 'r') as f:
    csv_data = csv.reader(f)
    for record in csv_data:
        try:
            student_id = record[0]
            student = Student.objects.get(invitation_id=student_id)
            enrollment = SKillOfferingEnrollment.objects.filter(
                is_mandatory=True,
                student_id=student.id,
                skill_offering__knowledge_partner_id=59
            ).order_by('-created').first()
            if not enrollment:
                writer.writerow(record + [None,'Not subscribed'])
            else:
                progress = SKillOfferingEnrollmentProgress.objects.filter(skill_offering_enrollment_id=enrollment.id).order_by('-created').first()
                if not progress:
                    writer.writerow(record + [None,'No progress'])
                else:
                    writer.writerow(record + [progress.progress_percentage])

        except Student.DoesNotExist:
            writer.writerow(record + [None,'Student Not found'])
        except Exception as e:
            writer.writerow(record + [None,'Exception-' + str(e)])
        except Exception as e:
            writer.writerow(record + [None,'Exception-' + str(e)])


