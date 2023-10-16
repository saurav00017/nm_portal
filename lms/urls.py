from django.urls import path
from .clients.views import lms_client, lms_clients, lms_clients_dropdown, lms_client_api_check, lms_client_key_reset
from .courses.views import lms_courses, lms_course_details, lms_course_update
from .apis.views import api_login, publish_course, list_courses, student_tracking, api_token_refresh, student_check
from rest_framework_simplejwt.views import TokenRefreshView
from .subscription.views import lms_course_subscription, lms_course_subscribed_list, lms_course_subscribed_watch_url
from .views import assessment_data_check, assessment_data_csv_report
urlpatterns = [
    path('client/', lms_client),
    path('client/<int:client_id>/', lms_client),
    path('client/<int:client_id>/reset/secret/key/', lms_client_key_reset),
    path('clients/', lms_clients),
    path('clients-dropdown/', lms_clients_dropdown),
    path('courses/', lms_courses),
    path('course/subscribe/', lms_course_subscription),
    path('courses/subscribe/', lms_course_subscribed_list),
    path('course/subscribed/watch-url/', lms_course_subscribed_watch_url),
    path('course/details/<int:course_id>/', lms_course_details),
    path('course/update/<int:course_id>/', lms_course_update),


    # LMS Client APIs
    path('client/token/', api_login),
    path('client/token/refresh/', api_token_refresh),
    path('client/course/publish/', publish_course),
    path('client/courses/', list_courses),
    path('client/course/xf/', student_tracking),
    path('client/course/student/check/', student_check),
    path('client/api/integration/check/', lms_client_api_check),

    # development mode
    path('assessment/data/check/', assessment_data_check),
    path('assessment/data/export/csv/', assessment_data_csv_report),



]
