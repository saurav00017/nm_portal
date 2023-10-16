from django.urls import path
from .views import (get_districts, get_affiliated_universities, get_college_registration_dropdowns,
                    get_student_registration_dropdowns, check_username, training_partners, get_skill_offering_dropdowns,
                    get_skill_offering_list, get_colleges_list, branches, zones, kp_list, link_partner_list)

from .announcements.views import announcements_list, announcements_update
from .portal_announcements.views import portal_announcements_list
from .ceritifcate.views import certificate_image, certificate_url_token
urlpatterns = [
    path('districts/', get_districts),
    path('affiliated-universities/', get_affiliated_universities),
    path('registration-dropdowns/', get_college_registration_dropdowns),
    path('student-registration-dropdowns/', get_student_registration_dropdowns),
    path('check-username/', check_username),
    path('training-partners/', training_partners),
    path('skill-offering/dropdown/', get_skill_offering_dropdowns),
    path('knowledge-partner/list/', kp_list),
    path('link-partner/list/', link_partner_list),
    path('skill-offering/list/', get_skill_offering_list),
    path('colleges/list/', get_colleges_list),
    path('branches', branches),
    path('zones', zones),
    path('announcements/list/', announcements_list),
    path('announcements/update/', announcements_update),
    path('portal/announcements/list/', portal_announcements_list),
    # certificate
    path('certificate/image/', certificate_image),
    path('certificate/token/', certificate_url_token),

]
