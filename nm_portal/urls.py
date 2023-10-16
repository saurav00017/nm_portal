"""nm_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from reports.mandatory_courses.views import update_mandatory_courses
from django.contrib import admin

from lms.subscription.cambridge_api import nm_student_details_to_cambridge
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import HttpResponse
from users.views import login, profile_details, change_password, forgot_username, forgot_password, forgot_password_reset
from users.views_v2 import request_otp_for_login_v2, verify_login_with_otp_v2
from users.eoi.views import eoi_otp, eoi_otp_verification, eoi_details, eoi_list, eoi_admin_details, eoi_details_v2
admin.site.site_header = "Naan Mudhalvan"
admin.site.index_title = "Naan Mudhalvan"
admin.site.site_title = "Naan Mudhalvan"


def demo_page(request):
    return HttpResponse("<h1>Forbidden</h1>")


urlpatterns = [

    path('upload/mandatory/courses/', update_mandatory_courses),
    path('api/v1/student/sso/check/', nm_student_details_to_cambridge),
    path('admin/', admin.site.urls),
    path('', demo_page),


    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # API V2
    path('api/v2/login/otp/request/', request_otp_for_login_v2),
    path('api/v2/login/otp/verify/', verify_login_with_otp_v2),
    # API V1
    # Digi Locker
    path('api/v1/digi/locker/', include('digi_locker.urls')),

    path('api/v1/login/', login),
    path('api/v1/forgot/username/', forgot_username),
    path('api/v1/forgot/password/', forgot_password),
    path('api/v1/forgot/password/reset/', forgot_password_reset),
    path('api/v1/token/refresh/', TokenRefreshView.as_view()),
    path('api/v1/user/profile-details/', profile_details),
    path('api/v1/user/password/update/', change_password),
    # EOI
    path('api/v1/eoi/otp/', eoi_otp),
    path('api/v1/eoi/otp/verification/', eoi_otp_verification),
    path('api/v1/eoi/admin/list/', eoi_list),
    path('api/v1/eoi/admin/details/', eoi_admin_details),
    path('api/v1/eoi/details/', eoi_details),
    path('api/v1/eoi/detailsV2/', eoi_details_v2),
    # # College
    path('api/v1/college/', include('college.urls')),
    path('api/v1/student/', include('student.urls')),
    path('api/v1/data/', include('datarepo.urls')),
    path('api/v1/lms/', include('lms.urls')),
    path('api/v1/reports/', include('reports.urls')),
    path('api/v1/skillofferings/', include('skillofferings.urls')),
    path('api/v1/mmm/', include('mmm.urls')),
    path('api/v1/simple_courses/', include('simple.urls')),
    path('psychometric-test/', include('psychometric.urls')),
    path('api/v1/kp/', include('kp.urls')),
    path('api/v1/fs/', include('fs.urls')),

    path('api/v1/simple/', include('simple.urls')),
    path('api/v1/industry/', include('industry_partners.urls')),
    path('api/v1/placements/', include('placements.urls')),

]
#
# ## Cambridge Student SSO
# from lms.subscription.cambridge_api import nm_student_details_to_cambridge
# urlpatterns += [
#      path('api/v1/student/sso/check/', nm_student_details_to_cambridge),
#
#  ]

if settings.LOCAL_TEST:
    urlpatterns = urlpatterns + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
