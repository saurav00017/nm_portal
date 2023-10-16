college_code_data = """1101
1105
1108
1111
1120
1123
1124
1125
1126
1127
1128
1133
2101
2102
2105
2106
2109
2111
2113
2117
2119
2120
2124
2126
2128
1114
2115
2129
5134
1106
2112
1
2104
1107
1138
2108
3101
3107
3108
3110
3115
3116
3118
3128
3105
3114
3111
2
3103
3121
3125
4101
4103
4106
4107
4108
4114
4115
4116
4117
4118
4120
4121
4123
4126
4127
4130
4
3126
1103"""
college_code_list = str(college_code_data).split("\n")
print(len(college_code_list))
print(college_code_list)
from lms.models import StudentCourse

students_courses = StudentCourse.objects.filter(
    lms_client_id=6,
).exclude(student__college__college_code__in=college_code_list, subscription_on=None)
import os
import csv
from django.conf import settings
file = open(os.path.join(settings.BASE_DIR, "scripts/new/lms/lnt_data.csv"), 'w')
writer = csv.writer(file)

data = students_courses.values_list('course__course_unique_code', 'course__course_name', 'student__invitation_id', 'subscription_reference_id', 'subscription_on')

writer.writerow(['course_unique_id', 'course_name', 'student_id', 'subscription_reference_id', 'subscription_on'])

writer.writerows(list(data))