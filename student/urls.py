from django.urls import path

from .registration.views import invite_student, student_registration, confirm_registration_payment, \
    resend_student_invites, student_bulk_invites, pass_out_student_registration
from .views import (list_students, student, upload_caste_certificate,
                    students, edit_student, bulk_students_verify,
                    list_students_with_basic_info, list_branches, list_sem, update_student_course_assessment_details, update_student_course_assessment_testscores, list_students_with_basic_info_faculty)

from .college_upload.views import step_1_upload_student_csv, student_bulk_upload_history
from .file_upload.views import step_1_upload_file, step_2_upload_file_list, step_3_upload_file_celery_initiate, step_4_upload_file_confirmation

urlpatterns = [
    path('invite/', invite_student),
    path('registration/pass-out/', pass_out_student_registration),
    path('invite/bulk/', student_bulk_invites),
    path('invite/<str:invitation_id>/', student_registration),
    path('registration/payment-confirmation/', confirm_registration_payment),
    path('registration/resend-student-invites/', resend_student_invites),
    path('list/', list_students),
    path('students/', students),
    path('student/edit/<int:student_id>', edit_student),
    path('details/<int:student_id>/', student),
    path('upload/certificate/', upload_caste_certificate),
    path('bulk_students_verify', bulk_students_verify),

    path('bulk-upload-file/', step_1_upload_file),
    path('bulk-upload-file/list/', step_2_upload_file_list),
    path('bulk-upload-file/celery-initiate/',
         step_3_upload_file_celery_initiate),
    path('bulk-upload-file/confirmation/', step_4_upload_file_confirmation),
    path('filters/students/', list_students_with_basic_info),
    path('filters/branches/', list_branches),
    path('filters/sem/', list_sem),
    path('course/assessment/details/update/',
         update_student_course_assessment_details),

    # Bulk Upload
    path('bulk/upload/', step_1_upload_student_csv),
    path('bulk/upload/history/', student_bulk_upload_history),

    # URLS's Created by anil
    #     path('FSC/', FacultyStudentCourse,
    #          name="student course with faculty"),
    #     path('scoreupdate/', TableViewSet,
    #          name="student course with faculty"),
    path('course/assessment/details/score/',
         update_student_course_assessment_testscores),
    path('course/assessment/details/update/faculty',
         list_students_with_basic_info_faculty)

]
