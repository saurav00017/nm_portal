from .launch.views import lms_course_launch_access_url

from django.urls import path
from .views import simple_courses_list

urlpatterns = [
    path('courses/', simple_courses_list),
    path('course/launch/url/', lms_course_launch_access_url),
]
