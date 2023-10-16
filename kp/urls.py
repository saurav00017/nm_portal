from django.urls import path
from .views import kps, kp, kp_credentials, kp_user

urlpatterns = [
    path('kps/', kps),
    path('', kp),
    path('<int:kp_id>/', kp),
    path('<int:kp_id>/credentials/', kp_credentials),
    path('<int:kp_id>/user/', kp_user),
]
