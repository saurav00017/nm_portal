from django.contrib import admin

from .models import Specialisation, Technology, SubTechnology, SKillOffering, SKillOfferingEnrollment, \
    SKillOfferingEnrollmentProgress, MandatoryCourse, CourseBulkUpload, FeedBack, SKillOfferingEnrollmentCertificate


@admin.register(Specialisation)
class SpecialisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(SubTechnology)
class SubTechnologyAdmin(admin.ModelAdmin):
    list_display = ('id', 'tech', 'name')
    list_filter = ('tech',)
    search_fields = ('name',)


@admin.register(SKillOffering)
class SKillOfferingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'knowledge_partner',
        'lms_course',
        'course_name',
        'technology',
        'sub_technology',
        'mode_of_delivery',
        'duration',
        'cost',
        'link',
        'is_mandatory',
        'lms_course',
        'offering_type',
        'offering_kind',
    )
    search_fields = ['lms_course__course_unique_code', 'course_name']
    list_filter = (
        'is_mandatory',
        'offering_type',
        'offering_kind',
        'knowledge_partner',
        'technology',
        'sub_technology',
        'lms_course',
    )
    raw_id_fields = ('specialization', 'branch', 'year_of_study', 'lms_course')


@admin.register(SKillOfferingEnrollment)
class SKillOfferingEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'college',
        'knowledge_partner',
        'skill_offering',
        'lms_course',
        'created',
        'updated',
        'status',
        'offering_type',
        'offering_kind',
        'comment',
        'is_mandatory',
    )
    list_filter = (
        'knowledge_partner',
        'lms_course',
        'created',
        'updated',
    )
    search_fields = ['student__email']
    raw_id_fields = ['knowledge_partner', 'lms_course', 'student', 'college', 'skill_offering']


@admin.register(SKillOfferingEnrollmentProgress)
class SKillOfferingEnrollmentProgressAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'skill_offering_enrollment',
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
        'knowledge_partner',
        'created',
        'updated',
        'assessment_status',
        'course_complete',
        'certificate_issued',
        'certificate_issued_at',
    )
    search_fields = [
        'skill_offering_enrollment__student__invitation_id',
        'skill_offering_enrollment__student__email',
        'skill_offering_enrollment__student__phone_number',
    ]
    raw_id_fields = ['knowledge_partner', 'skill_offering_enrollment']


@admin.register(SKillOfferingEnrollmentCertificate)
class SKillOfferingEnrollmentCertificateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'certificate_id',
        'certificate_no',
        'skill_offering_enrollment',
        'knowledge_partner',
        'created',
        'updated',)

    raw_id_fields = ['knowledge_partner', 'skill_offering_enrollment']

    search_fields = [
        'certificate_id',
        'certificate_no',
        'skill_offering_enrollment__student__invitation_id',
    ]
    list_filter = (
        'knowledge_partner',
    )


@admin.register(MandatoryCourse)
class MandatoryCourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'college',
        'skill_offering',
        'branch',
        'sem',
        'count',
        'created',
        'updated',
    )
    raw_id_fields = ['college', 'skill_offering']


@admin.register(CourseBulkUpload)
class CourseBulkUploadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'skill_offering',
        'status',
        'created',
        'updated',
        'course_type',
    )
    raw_id_fields = ['skill_offering']
    list_filter = ['course_type']


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'enrollment_id',
        'student_id',
        'course_name',
        'quality_of_course',
        'quality_of_trainer',
        'created',
        'updated',
    )
    raw_id_fields = ['student', 'enrollment', 'skill_offering']

