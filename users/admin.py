from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, UserDetail, NMStaffDetails, EOIDetail, EOIRegistration, PhoneNumberOtp
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'account_role', 'name', 'email', 'mobile']
    list_filter = ['account_role']
    search_fields = ['username', 'name']


UserAdmin.fieldsets += (
    (
        'Custom fields', {
            'fields': (
                'account_role',
                'name', 'mobile')
        }
    ),
)

admin.site.register(User, CustomUserAdmin)


@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'college', 'student']
    raw_id_fields = ['user', 'college', 'student']
    search_fields = ['college__college_code', 'student__roll_no', 'user__username']

@admin.register(NMStaffDetails)
class NMStaffDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'district' ]
    raw_id_fields = ['user']


@admin.register(EOIRegistration)
class EOIRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user' ]
    raw_id_fields = ['user']


@admin.register(EOIDetail)
class EOIDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'user' ]
    raw_id_fields = ['user']


@admin.register(PhoneNumberOtp)
class PhoneNumberOtpAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'verification_code', 'verification_request_count', 'created', 'updated']
