from django.contrib import admin
from .models import StudentPlacementDetail
# Register your models here.

@admin.register(StudentPlacementDetail)
class StudentPlacementDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'created', 'updated']
    raw_id_fields = ['student']