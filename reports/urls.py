from django.urls import path
from .views import list_district_reports, list_college_reports, upload_college_data, upload_college_data1, \
    college_details, launch_stats

from .mandatory_courses.views import mandatory_courses_report, mandatory_course_with_student_report, student_mandatory_courses
from .colleges.views import list_college_report
from .skill_offerings.views import skill_offerings_overview_report, skill_offerings_detail_report
from .coursera.views import generate_coursera_report, assessment_status_update
urlpatterns = [
    path('districts/', list_district_reports),
    path('district/colleges/', list_college_reports),
    path('upload/colleges/', upload_college_data),
    path('upload/colleges1/', upload_college_data1),
    path('college/details/', college_details),
    path('launch/stats/', launch_stats),
    path('mandatory/courses/', mandatory_courses_report),
    path('mandatory/courses/simple/', mandatory_course_with_student_report),
    path('mandatory/courses/students/', student_mandatory_courses),
    path('colleges/mandatory/course/info/', list_college_report),
    # Skill offerings
    path('skill-offerings/overview/', skill_offerings_overview_report),
    path('skill-offerings/detail/', skill_offerings_detail_report),
    path('coursera/generate/report/', generate_coursera_report),
    path('coursera/assessment/status/update/', assessment_status_update),

]
