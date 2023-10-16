from django.contrib import admin
from .models import Student, CollegeTemporaryFileUpload, StudentPaymentDetail, StudentRegistrationStepOne, TemporaryFileUpload


# Register your models here.


@admin.register(StudentRegistrationStepOne)
class StudentRegistrationStepOneAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'total_count', 'valid_count', 'invalid_count', 'already_exist_count', 'is_mailed',
                    'user', 'created']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id',  'roll_no','invitation_id','phone_number', 'email', 'sem', 'registration_status','college_id', 'college', 'first_name',
                    'last_name',
                     'created']
    list_select_related = ['college']
    list_filter = ['sem', 'rbranch', 'branch', 'degree', 'payment_status', 'registration_status']

    raw_id_fields = ['step_one', 'rbranch', 'college', 'affiliated_university', 'added_by']
    search_fields = ['email', 'roll_no', 'invitation_id', 'phone_number', 'college__college_name']

#

@admin.register(StudentPaymentDetail)
class StudentPaymentDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'razorpay_order_id', 'razorpay_payment_id']


@admin.register(TemporaryFileUpload)
class TemporaryFileUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'college_type', 'status', 'created', 'updated']
    list_filter = ['college_type', 'status']

@admin.register(CollegeTemporaryFileUpload)
class CollegeTemporaryFileUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'college_id', 'status', 'created', 'updated']
    list_filter = ['college_type']
