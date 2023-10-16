
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
from college.models import College

courses = MandatoryCourse.objects.filter(skill_offering_id__in=[2221,2222,2223,2224]).distinct("skill_offering_id")

collegeCodes = ["1","2","4","1101","1102","1103","1105","1106","1107","1108","1111","1113","1114","1118","1120","1121","1123","1124","1125","1126","1127","1128","1133","1135","1136","1137","1138","1139","2101","2102","2103","2104","2105","2106","2108","2109","2111","2112","2113","2115","2117","2118","2119","2120","2124","2126","2128","2129","2131","3101","3103","3105","3107","3108","3110","3111","3112","3113","3114","3115","3116","3117","3118","3120","3121","3124","3125","3126","3128","3129","3131","3133","4101","4103","4106","4107","4108","4114","4115","4116","4117","4118","4120","4121","4123","4126","4127","4130","5134"]

header = ['First name', 'Last name', 'Email id', 'Phone number', 'Is minor (yes/NO)', 'Gender', 'Grade', 'Institution/University Code(AISHE CODE)']

collegeIds = []

for c in collegeCodes:
    college = College.objects.get(college_code=c)
    collegeIds.append(college.id)

for mc in courses:
    students_assigned = SKillOfferingEnrollment.objects.select_related('student', 'college', 'skill_offering').filter(
            skill_offering_id=mc.skill_offering_id, college_id__in=collegeIds, student_id__isnull=False)
    print(students_assigned.count())
    with open('scripts/karthik/infosys/students_' + str(mc.skill_offering_id) + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for student in students_assigned:
            print(student.student)
            _full_name = student.student.aadhar_number
            full_name = str(_full_name).split(" ", 1)
            first_name = None
            last_name = None
            if len(full_name) > 1:
                first_name = full_name[0]
                last_name = full_name[1]
            else:
                first_name = _full_name

            gender = 'Male' if student.student.gender == 1 else 'Female' if student.student.gender == 2 else 'Other' if student.student.gender == 3 else 'Do not wish to disclose'

            data = [first_name, last_name, student.student.email, student.student.phone_number, "NO",gender, 'Graduate', "U-U-" + str(student.college.college_code).replace(" ", "")]

            writer.writerow(data)