from django.contrib import admin

from .models import FSCourse, FSEnrollment, FSEnrollmentProgress


@admin.register(FSCourse)
class FSCourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'knowledge_partner',
        'name',
        'description',
        'details',
        'status',
    )
    list_filter = ('knowledge_partner',)
    search_fields = ('name',)


@admin.register(FSEnrollment)
class FSEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'college',
        'knowledge_partner',
        'fs_course',
        'created',
        'updated',
        'status',
        'comment',
        'enrollment_type',
    )
    list_filter = (
        'knowledge_partner',
        'fs_course',
        'created',
        'updated',
    )


@admin.register(FSEnrollmentProgress)
class FSEnrollmentProgressAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fs_course',
        'knowledge_partner',
        'created',
        'updated',
        'progress_percentage',
        'assessment_status',
        'course_complete',
        'certificate_issued',
        'certificate_issued_at',
    )
    list_filter = (
        'fs_course',
        'knowledge_partner',
        'created',
        'updated',
        'assessment_status',
        'course_complete',
        'certificate_issued',
        'certificate_issued_at',
    )