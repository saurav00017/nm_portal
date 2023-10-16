from django.contrib import admin

from .models import PsychometricPartner, PsychometricResult


@admin.register(PsychometricPartner)
class PsychometricPartnerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'client_secret',
        'client_key',
        'created_at',
        'updated_at',
        'status',
    )
    list_filter = ('created_at', 'updated_at', 'status')
    raw_id_fields = ['client']
    date_hierarchy = 'created_at'


@admin.register(PsychometricResult)
class PsychometricResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'student', 'college', 'result')
    list_filter = ('client',)
    raw_id_fields = ['student', 'college']
