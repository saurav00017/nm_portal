from skillofferings.models import SKillOfferingEnrollmentProgress

all_progress = SKillOfferingEnrollmentProgress.objects.filter(
    skill_offering_enrollment__is_mandatory=1,
    skill_offering_enrollment__student_id__isnull=False,
).exclude(assessment_data=None)
import csv
import os
import json
from django.conf import  settings
file_name = "scripts/new/mandatory/assessment_data/in_corrent_data3.csv"
print(all_progress.count())

csv_data = 'progress_id,skill_offering_id,course_name,student_id,student_unique_id.failed reason,assessment_data'
total_count = all_progress.count()
print('total_count', total_count)
for index, record in enumerate(all_progress):
    # if index == 3:
    #     break
    assessment_data = record.assessment_data
    print("Pending ---> ", total_count - index, type(assessment_data))
    if isinstance(assessment_data, str):
        assessment_data = json.loads(assessment_data)
    if isinstance(assessment_data, dict):
        record.assessment_data = [assessment_data]
        record.save()
        assessment_data = record.assessment_data
    if isinstance(assessment_data, list):

        Failed_status = False
        for data_record in assessment_data:
            if 'score' not in data_record:
                Failed_status = 'score not in record'
            else:
                try:
                    score = float(data_record['score'])
                except Exception as e:
                    score = None
                    Failed_status = f'score - {e}'

            if 'correct_answers' not in data_record:
                Failed_status = 'correct_answers not in record'
            else:
                try:
                    correct_answers = int(data_record['correct_answers'])
                except Exception as e:
                    correct_answers = None
                    Failed_status = f'correct_answers - {e}'

            if 'total_questions' not in data_record:
                Failed_status = 'total_questions not in record'
            else:
                try:
                    total_questions = int(data_record['total_questions'])
                except Exception as e:
                    total_questions = None
                    Failed_status = f'total_questions - {e}'

            if 'serial' not in data_record:
                Failed_status = 'serial1'
            else:
                try:

                    serial = int(data_record['serial'])
                except Exception as e:
                    serial = None
                    Failed_status = f'serial2-{e}'

            if 'attempt' not in data_record:
                Failed_status = 'attempt not in record'
            else:
                try:
                    attempt = int(data_record['attempt'])
                except Exception as e:
                    attempt = None
                    Failed_status = f'attempt - {e}'

        if Failed_status:
            print("Failed", Failed_status)
            enrollment = record.skill_offering_enrollment
            csv_data += '\n' \
                        f'{record.id},' \
                        f'{enrollment.skill_offering_id},' \
                        f'{enrollment.skill_offering.course_name if enrollment.skill_offering_id else None},' \
                        f'{enrollment.student_id},' \
                        f'{enrollment.student.invitation_id if enrollment.student_id else None},' \
                        f'{Failed_status},'\
                        f'{json.dumps(assessment_data)}'
    else:
        print("Failed")
        enrollment = record.skill_offering_enrollment
        csv_data += '\n' \
                    f'{record.id},' \
                    f'{enrollment.skill_offering_id},' \
                    f'{enrollment.skill_offering.course_name if enrollment.skill_offering_id else None},' \
                    f'{enrollment.student_id},' \
                    f'{enrollment.student.invitation_id if enrollment.student_id else None},' \
                    f'Data type - {type(assessment_data)},' \
                    f'{assessment_data}'


with open(os.path.join(settings.BASE_DIR, file_name), 'w') as f:
    f.write(csv_data)
    f.close()