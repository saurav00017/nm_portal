from django.contrib import admin

from .models import SimpleCourse


@admin.register(SimpleCourse)
class SimpleCourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'knowledge_partner',
        'category',
        'name',
        'course_type',
        'link',
    )
    list_filter = ('knowledge_partner', 'category')
    search_fields = ('name',)
