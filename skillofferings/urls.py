from django.urls import path
from .views import specialisation_technologies, skill_offerings, skill_offering_enrollment, \
    skill_offering_enrollment_list, skill_offering_enrollment_update, skill_offering_enrollment_progress, \
    skill_offerings_detail, skill_offering, skill_offering_dropdowns
from .spoc.views import mandatory_courses_list, mandatory_course, college_finish_allocation
from .coursera.views import upload_coursera_file, coursera_file_upload_list
from .microsoft.views import upload_microsoft_file, microsoft_file_upload_list
from .feed_back.views import feed_back
from .infosys.views import upload_infosys_file, infosys_file_upload_list
from .mandatory_courses.views import nm_mandatory_course, nm_mandatory_course_list
from .certificate.views import validate, view

urlpatterns = [
    path('specialisation_technologies/', specialisation_technologies),
    path('skill_offerings/', skill_offerings),
    path('skill_offering/', skill_offerings_detail),
    path('skill_offering/dropdowns/', skill_offering_dropdowns),
    path('add/', skill_offering),
    path('update/', skill_offering),
    path('skill_offering_enrollment/', skill_offering_enrollment),
    path('skill_offering_enrollment_list/', skill_offering_enrollment_list),
    path('skill_offering_enrollment_update/', skill_offering_enrollment_update),
    path('progress/', skill_offering_enrollment_progress),
    path('mandatory/courses/', mandatory_courses_list),
    path('mandatory/course/', mandatory_course),
    path('nm/mandatory/courses/list/', nm_mandatory_course_list),
    path('nm/mandatory/course/', nm_mandatory_course),
    path('mandatory/course/college/finish/allocation/', college_finish_allocation),

    path('coursera/upload/', upload_coursera_file),
    path('coursera/list/', coursera_file_upload_list),
    path('microsoft/upload/', upload_microsoft_file),
    path('microsoft/list/', microsoft_file_upload_list),
    path('infosys/upload/', upload_infosys_file),
    path('infosys/list/', infosys_file_upload_list),
    path('feed_back/', feed_back),

    path('certificate/validate', validate),
    path('certificate/view', view),
]
