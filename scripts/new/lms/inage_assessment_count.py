from skillofferings.models import SKillOfferingEnrollmentProgress, SKillOfferingEnrollment
from college.models import College
from student.models import Student
import csv
college_filename = 'scripts/mandatory/sa/z170.csv'
college_codes = []
with open('/opt/nm/NM_portal_backend/nm_portal/scripts/mandatory/sa/z170.csv', 'r') as file:
    data = csv.reader(file)
    for record in data:
        if record:
            college_code = record[0]
            if college_code:
                college_codes.append(college_code)

college_ids = College.objects.values_list('id', flat=True).filter(college_code__in=college_codes)

student_ids = Student.objects.values_list('id', flat=True).filter(college_id__in=college_ids)

enrollment_list = SKillOfferingEnrollment.objects.filter(
    skill_offering_id=2226,
    student_id__in=student_ids
)
enrollment_ids = enrollment_list.values_list('id', flat=True)

enrollment_progress_list = SKillOfferingEnrollmentProgress.objects.values('assessment_data').filter(
    skill_offering_enrollment_id__in=enrollment_ids
)

total_count = enrollment_progress_list.count()
unique_count = enrollment_progress_list.distinct(
    'skill_offering_enrollment__skill_offering_id',
    'skill_offering_enrollment__student_id',
).count()
counter = {}
serial_level_counter = {}
print("Colleges count", len(college_ids))
print("Total count", enrollment_progress_list.count())
print("Unique count", unique_count)
print("Duplicate count", total_count - unique_count)
for record in enrollment_progress_list:
    assessment_data = record['assessment_data']
    serial_ids = []
    if assessment_data and type(assessment_data) == dict:
        serial = assessment_data['serial']
        if serial not in serial_ids:
            serial_ids.append(serial)

        serials_key = str([assessment_data['serial']])
        if serials_key in counter:
            counter[serials_key] += 1
        else:
            counter[serials_key] = 1

    elif assessment_data and type(assessment_data) == list:
        serials_list = []
        for assessment in assessment_data:
            serial = assessment['serial']
            serials_list.append(assessment['serial'])

            if serial not in serial_ids:
                serial_ids.append(serial)

        if serials_list and len(serials_list) > 1:
            serials_list = list(set(serials_list))

        if serials_list:
            serials_key = str(serials_list)
        else:
            serials_key = "None"
        if serials_key in counter:
            counter[serials_key] += 1
        else:
            counter[serials_key] = 1
         #
        # if assessment_data and type(assessment_data) == list:
        #     len_assessment_data = len(assessment_data)
        #     if len_assessment_data in counter:
        #         counter[len_assessment_data] += 1
        #     else:
        #         counter[len_assessment_data] = 1
        # elif assessment_data and type(assessment_data) == dict:
        #     if 1 in counter:
        #         counter[1] += 1
        #     else:
        #         counter[1] = 1
    else:
        if 'no_single_assessment_submit' in counter:
            counter['no_single_assessment_submit'] += 1
        else:
            counter['no_single_assessment_submit'] = 1

    for serial_id in serial_ids:

        if serial_id in serial_level_counter:
            serial_level_counter[serial_id] += 1
        else:
            serial_level_counter[serial_id] = 1

print("\n\n======= Combination Report ===========")
print('count  -  Assessment Serial',)
for key, value in counter.items():
    print(f"{value} - {key}")


print("\n\n======= Individual Report ===========")
serial_level_counter['None'] = counter['no_single_assessment_submit']
for key, value in serial_level_counter.items():

    print(f"Assessment ({key}) - {value}")