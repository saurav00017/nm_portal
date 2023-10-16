from django.urls import path
from .views import start_test

urlpatterns = [
    path('start_test/', start_test),
]
