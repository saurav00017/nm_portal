from django.contrib import admin
from .models import CollegeReport, DistrictReport
# Register your models here.


@admin.register(DistrictReport)
class DistrictReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'district', 'total_no_of_colleges']


@admin.register(CollegeReport)
class CollegeReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'district', 'college', 'total_no_of_students']
    list_filter = ['district']
