import os
from django.conf import settings
import csv
import json

file = "scripts/mandatory/assignments/data_validation/assessment_data.csv"

"""
0 'is_mandatory', 
1 'id', 
2 'progress_percentage', 
3 'assessment_data',
 4. ia_count,
 'skill_offering_enrollment_id', 'skill_offering_enrollment__skill_offering_id', 'skill_offering__course_name', 'skill_offering__course_code', 'student_id', 'skill_offering_enrollment__skill_offering__knowledge_partner_id', 'skill_offering_enrollment__skill_offering__knowledge_partner__name'"""

valid_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/data_validation/valid_data.csv'), 'w')
valid_writer = csv.writer(valid_file)

invalid_file = open(os.path.join(settings.BASE_DIR, 'scripts/mandatory/assignments/data_validation/invalid_data.csv'), 'w')
invalid_writer = csv.writer(invalid_file)

with open(file, 'r') as file:
    data = csv.reader(file)
    header = next(data)
    final_header = ['ia_count', 'total_sum', 'final_score', 'progress_percentage'] + header
    invalid_writer.writerow(final_header)
    valid_writer.writerow(final_header)
    index = 0
    for row in data:
        index += 1
        print("Index at --> ", index)
        try:
            if row[3] != '':
                data = json.loads(str(row[3]).replace("'", '"').replace("None", 'null'))
                progress_percentage = row[2]
                score_data = {}
                for record in data:
                    if 'serial' in record and 'score' in record:
                        # print("Flag 1")
                        if record['serial'] in score_data:
                            # print("Flag 2")
                            if score_data[record['serial']] < record['score']:
                                score_data[record['serial']] = record['score']
                            else:
                                score_data[record['serial']] = record['score']
                        else:
                            score_data[record['serial']] = record['score']

                scores_list = score_data.values()
                total_sum = sum(scores_list)
                ia_count = int(row[4]) if row[4] not in ['', None, 0] else len(scores_list)
                assessment_count = scores_list
                final_value = total_sum/ia_count

                final_data = [ia_count, total_sum, final_value, float(progress_percentage)] + row
                if ia_count:
                    if round(float(progress_percentage), 2) == round(total_sum/ia_count, 2):
                        # print(row[1], True, sep=" ==> ")
                        valid_writer.writerow(final_data)
                        continue
                invalid_writer.writerow(final_data)
            invalid_writer.writerow([None,None,None,None]+ row)
        except Exception as e:
            print(e, row[4])