from django.contrib import admin
from .models import LMSClient, Course, CourseHistory, StudentCourse, LmsApiLog
# Register your models here.


@admin.register(LMSClient)
class LMSClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'client_key']
    raw_id_fields = ['user']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'course_unique_code', 'course_name', 'course_type']
    list_filter = ['lms_client']
    search_fields = ['course_unique_code']
    raw_id_fields = ['lms_client', 'approved_by']


@admin.register(CourseHistory)
class CourseHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'created']


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_id', 'student', 'course_id', 'course', 'created']
    raw_id_fields = ['course', 'student']
    search_fields = ['student__roll_no', 'student__invitation_id']
    list_filter = ['course', 'lms_client']


@admin.register(LmsApiLog)
class LmsApiLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'lms_client', 'status_code', 'sub_url', 'created']
    search_fields = ['response', 'payload']
    list_filter = ['sub_url', 'status_code', 'lms_client']
