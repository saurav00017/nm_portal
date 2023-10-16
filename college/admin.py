from django.contrib import admin
from .models import RegistrationStepOne, College, CollegeSubscription, CollegeOtpVerification, CollegeFaculty, \
    FacultyFDPDetails


# Register your models here.


@admin.register(RegistrationStepOne)
class RegistrationStepOneAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'total_count', 'valid_count', 'invalid_count', 'already_exist_count', 'is_mailed',
                    'user', 'created']


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['id', 'invitation_id', 'status', 'college_code', 'college_name', 'is_mailed', 'district', 'pincode',
                    'created']
    list_filter = ['district', 'status', 'college_type']
    search_fields = ['id', 'college_code', 'college_name']


@admin.register(CollegeSubscription)
class CollegeSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'razorpay_order_id', 'razorpay_payment_id', 'registration_fee']


@admin.register(CollegeOtpVerification)
class CollegeOtpVerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'college', 'otp', 'otp_type', 'created']


@admin.register(CollegeFaculty)
class CollegeFacultyAdmin(admin.ModelAdmin):
    list_display = ['id', 'college', 'branch', 'designation', 'name', 'email', 'phone_number']


@admin.register(FacultyFDPDetails)
class FacultyFDPDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'faculty', 'details', 'technology']
