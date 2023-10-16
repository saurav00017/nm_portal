from django.urls import path
from .registration.views import college_invites, college_registration, confirm_registration_payment, mail_test, \
    resend_college_invites
from .views import colleges, college, list_colleges_dropdown, college_counter, college_send_otp, \
    college_otp_confirmation, college_external_assessment, faculty, faculties, colleges_list, send_email_to_faculty

urlpatterns = [
    # registrations
    path('registration-invites/', college_invites),
    path('registration/invitation-<str:invitation_id>/', college_registration),
    path('registration/payment-confirmation/', confirm_registration_payment),
    path('registration/resend_college_invites/', resend_college_invites),

    # Colleges
    path('list/', colleges),
    path('details/<int:college_id>/', college),
    path('dropdown-list/', list_colleges_dropdown),
    path('mail_test/', mail_test),
    path('counters/', college_counter),
    path('otp/send/', college_send_otp),
    path('otp/confirmation/', college_otp_confirmation),
    path('external/assessment/', college_external_assessment),
    path('faculty/', faculty),
    path('faculties/', faculties),
    path('colleges_list/', colleges_list),
    path('sending_mail_to_faculty/', send_email_to_faculty)
]
