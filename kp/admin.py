# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import KnowledgePartner, LinkPartner


@admin.register(KnowledgePartner)
class KnowledgePartnerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'lms_client',
        'logo',
        'user',
        'name',
        'description',
        'website',
        'is_fs',
    )
    list_filter = ['lms_client']
    search_fields = ('name',)
    raw_id_fields = ['user']


@admin.register(LinkPartner)
class LinkPartnerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'website',
    )


