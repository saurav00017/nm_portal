import csv
import os
from django.conf import settings
from student.models import Student
from django.utils import  timezone
from skillofferings.models import SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
filename = "scripts/ingage/ARVR_Engg_report_05-12-22-Table.csv"

with open(os.path.join(settings.BASE_DIR, filename), 'r') as file:
    csv_data = csv.reader(file)
    print(next(csv_data))
    index = 0
    for row in csv_data:
        index +=1
        if index >= 5:
            break
        student_id = row[1]
        assessment_1 = row[2]
        assessment_2 = row[3]
        assessment_3 = row[4]
        assessment_4 = row[5]
        total_score = row[6]

        try:
            student = Student.objects.get(invitation_id=student_id)
            enrollment = SKillOfferingEnrollment.objects.get(
                student_id=student.id,
                skill_offering_id=2226,
                is_mandatory=True
            )

            progress = SKillOfferingEnrollmentProgress.objects.get(
                skill_offering_enrollment_id=enrollment.id
            )

            progress.progress_percentage = total_score
            assessment_data = progress.assessment_status
            if type(assessment_data) == dict:
                assessment_data = [assessment_data]
            if type(assessment_data) == list:
                temp = {}
                serial_1_records = list(filter(lambda x: x['serial'] == 1, assessment_data))
                serial_2_records = list(filter(lambda x: x['serial'] == 2, assessment_data))
                serial_3_records = list(filter(lambda x: x['serial'] == 3, assessment_data))
                serial_4_records = list(filter(lambda x: x['serial'] == 4, assessment_data))

                if serial_1_records:
                    serial_1_records = sorted(serial_1_records, key=lambda x: (x['attempt'], x['score']), reverse=True)
                    _serial_1 = serial_1_records[0]
                    if float(assessment_1) > _serial_1['score']:
                        assessment_data.append({
                            'serial': 1,
                            "attempt": int(_serial_1['attempt']) + 1,
                            "submitted_on": timezone.now(),
                            "score": float(assessment_1),
                            "created": "",
                            "updated": "",
                        })
                else:
                    assessment_data.append({
                        'serial': 1,
                        "attempt": 1,
                        "submitted_on": timezone.now(),
                        "score": float(assessment_1),
                        "created": "",
                        "updated": "",
                    })

                if serial_2_records:
                    serial_2_records = sorted(serial_2_records, key=lambda x: (x['attempt'], x['score']), reverse=True)
                    _serial = serial_2_records[0]
                    if float(assessment_2) > _serial['score']:
                        assessment_data.append({
                            'serial': 3,
                            "attempt": int(_serial['attempt']) + 1,
                            "submitted_on": timezone.now(),
                            "score": float(assessment_2),
                            "created": "",
                            "updated": "",
                        })
                else:
                    assessment_data.append({
                        'serial': 2,
                        "attempt": 1,
                        "submitted_on": timezone.now(),
                        "score": float(assessment_2),
                        "created": "",
                        "updated": "",
                    })

                if serial_3_records:
                    serial_3_records = sorted(serial_3_records, key=lambda x: (x['attempt'], x['score']), reverse=True)
                    _serial = serial_3_records[0]
                    if float(assessment_3) > _serial['score']:
                        assessment_data.append({
                            'serial': 3,
                            "attempt": int(_serial['attempt']) + 1,
                            "submitted_on": timezone.now(),
                            "score": float(assessment_3),
                            "created": "",
                            "updated": "",
                        })
                else:
                    assessment_data.append({
                        'serial': 3,
                        "attempt": 1,
                        "submitted_on": timezone.now(),
                        "score": float(assessment_3),
                        "created": "",
                        "updated": "",
                    })

                if serial_4_records:
                    serial_4_records = sorted(serial_4_records, key=lambda x: (x['attempt'], x['score']), reverse=True)
                    _serial = serial_4_records[0]
                    if float(assessment_4) > _serial['score']:
                        assessment_data.append({
                            'serial': 4,
                            "attempt": int(_serial['attempt']) + 1,
                            "submitted_on": timezone.now(),
                            "score": float(assessment_4),
                            "created": "",
                            "updated": "",
                        })
                else:
                    assessment_data.append({
                        'serial': 4,
                        "attempt": 1,
                        "submitted_on": timezone.now(),
                        "score": float(assessment_4),
                        "created": "",
                        "updated": "",
                    })

            print(assessment_data)

        except Exception as e:
            print("Error", e)

