from django.urls import path
from .views import fs_courses, enrollment, enrollments, progress

urlpatterns = [
    path('courses/', fs_courses),
    path('enrollment/', enrollment),
    path('enrollments/', enrollments),
    path('progress/', progress),
]
