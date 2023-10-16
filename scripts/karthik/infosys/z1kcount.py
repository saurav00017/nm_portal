from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv


header = ['id', 'student', 'student_name' 'college']

collegeCodes = ["1101","1105","1108","1111","1120","1123","1124","1125","1126","1127","1128","1133","2101","2102","2105","2106","2109","2111","2113","2117","2119","2120","2124","2126","2128","1114","2115","2129","5134","1106","2112","1","2104","1107","1138","2108","3101","3107","3108","3110","3115","3116","3118","3128","3105","3114","3111","2","3103","3121","3125","4101","4103","4106","4107","4108","4114","4115","4116","4117","4118","4120","4121","4123","4126","4127","4130","4","3126","1103"]

count = 0
with open('students_kps.csv', 'w', encoding='UTF8', newline='') as f:
    for code in collegeCodes:
        sks = SKillOfferingEnrollment.objects.filter(knowledge_partner_id=77, is_mandatory=1, college__college_code=code).distinct('student_id').select_related('student', 'skill_offering')
        for sk in sks:
            writer = csv.writer(f)
            if(sk.student == None):
                print(sk.id, " is Not none")
            else:
                writer.writerow([sk.id, sk.skill_offering.course_name, sk.student.id, sk.student.aadhar_number, sk.college_id])
        count += sks.count()

print(count)


