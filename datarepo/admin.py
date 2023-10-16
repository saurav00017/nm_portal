from django.contrib import admin

from .models import District, AffiliatedUniversity, Branch, YearOfStudy, SkillOffering, Zone,CollegeCategory, Announcement, PortalAnnouncement

@admin.register(CollegeCategory)
class CollegeCategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'district', 'name')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(AffiliatedUniversity)
class AffiliatedUniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(YearOfStudy)
class YearOfStudyAdmin(admin.ModelAdmin):
    list_display = ('id', 'year')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

@admin.register(PortalAnnouncement)
class PortalAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

@admin.register(SkillOffering)
class SkillOfferingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'skill_offering_for',
        'technology',
        'training_module',
        'specialization',
        'year_of_study',
        'live_training',
        'live_virtual_training',
        'certification',
        'created',
    )
    list_filter = ('created',)
