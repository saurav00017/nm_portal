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
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
from django.db.models import Sum

# mandatory_courses = MandatoryCourse.objects.filter(
#     college__college_code__in=college_code_list,
#     skill_offering__lms_course__lms_client=6
# )
# print(mandatory_courses.aggregate(Sum('count')))
#

print(SKillOfferingEnrollment.objects.filter(
    student__college__college_code__in=college_code_list,
    is_mandatory=1,
    skill_offering__lms_course__lms_client_id=6).count())