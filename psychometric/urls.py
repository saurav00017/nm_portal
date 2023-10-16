from django.urls import path
from .views import psychometric_token, psychometric_refresh, psychometric_results

urlpatterns = [
    path('token/', psychometric_token),
    path('token/refresh', psychometric_refresh),
    path('result', psychometric_results),

]
