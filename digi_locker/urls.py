
from django.urls import path
from .views import digi_locker_push, digi_locker_pull_certificate
urlpatterns = [
    path('push/', digi_locker_push),
    path('certificate/', digi_locker_pull_certificate),
]