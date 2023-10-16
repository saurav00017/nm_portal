# from kp.models import KnowledgePartner
# from skillofferings.models import SKillOffering
# import os
# import csv
# from django.conf import settings
# from lms.models import Course
# file = open(os.path.join(settings.BASE_DIR, 'scripts/courses/course_api_data.csv'), 'r')
# csv_data = csv.reader(file)
# counter = 0
# lms_client_id = None
# for record in csv_data:
#     course_code = record[0]
#     course_name = record[1]
#     try:
#         get_course = Course.objects.get(
#             lms_client_id=lms_client_id,
#             course_name=course_name
#         )
#     except Course.DoesNotExist:
#         get_course = Course.objects.create(
#             lms_client_id=lms_client_id,
#             course_type='ONLINE',
#             course_name=course_name,
#         )
#     get_course.course_unique_code=course_code
#     get_course.save()
#     skill_offerings = SKillOffering.objects.filter(course_name=course_name)
#     print(course_name, skill_offerings.count())
