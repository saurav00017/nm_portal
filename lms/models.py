from django.db import models

"""
StudentCourse Model
    user_id
    course_id
    

1. add fields

2 - endpoints
    1. /course/subscribe <- course_id -> 1. Check Token
        
"""
# Create your models here.


class LMSDevNames:
    TCS = 'tcs'
    COURSERA = 'coursera'
    CAMBRIDGE = 'cambridge'


class LMSClient(models.Model):
    client_key = models.CharField(max_length=255, null=True, blank=True)
    client_secret = models.CharField(max_length=255, null=True, blank=True)
    client_base_url = models.CharField(max_length=255, null=True, blank=True)
    lms_dev_name = models.CharField(max_length=255, null=True, blank=True)

    contact_name = models.CharField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=255, null=True, blank=True)
    contact_email = models.CharField(max_length=255, null=True, blank=True)
    client = models.CharField(max_length=255, null=True, blank=True)
    client_logo = models.ImageField(null=True, blank=True, upload_to='lms_clients')
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.client)


class CourseStatus:
    NEW = 0
    APPROVED = 1
    REJECTED = 2


class Course(models.Model):
    course_unique_code = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    course_type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    course_description = models.TextField(null=True, blank=True)
    course_content = models.JSONField(null=True, blank=True)
    course_objective = models.JSONField(null=True, blank=True)
    course_image_url = models.CharField(max_length=255, null=True, blank=True)
    partner_name = models.CharField(max_length=255, null=True, blank=True)
    instructor = models.CharField(max_length=255, null=True, blank=True)
    duration = models.FloatField(default=0, null=True, blank=True)
    number_of_videos = models.IntegerField(default=0)
    language = models.CharField(max_length=255, null=True, blank=True)
    main_stream = models.CharField(max_length=255, null=True, blank=True)
    sub_stream = models.CharField(max_length=255, null=True, blank=True)
    # course_outcomes = models.TextField(null=True, blank=True)
    system_requirements = models.CharField(max_length=255, null=True, blank=True)
    has_subtitles = models.BooleanField(default=False)
    reference_id = models.CharField(max_length=255, null=True, blank=True)
    lms_client = models.ForeignKey('lms.LMSClient', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    client_status = models.BooleanField(default=False)

    status = models.IntegerField(default=0)
    '''
    :status -> Course
    0 - new
    1 - Approved
    2 - Rejected
    '''
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.lms_client) + " - " + str(self.course_unique_code)


class RecordType:
    NEW = 0
    CHANGE_REQUEST = 1


class CourseType:
    ONLINE = 'ONLINE'
    CLASS_ROOM = 'CLASS ROOM'


class CourseHistory(models.Model):
    course = models.ForeignKey('lms.Course', on_delete=models.SET_NULL, null=True, blank=True)

    record_type = models.IntegerField(default=0)
    '''
    :record_type
    0 - new
    1 - change request
    '''
    # Fields
    course_unique_code = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    course_type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    course_description = models.TextField(null=True, blank=True)
    course_content = models.JSONField(null=True, blank=True)
    course_objective = models.JSONField(null=True, blank=True)
    course_image_url = models.CharField(max_length=255, null=True, blank=True)
    partner_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    instructor = models.CharField(max_length=255, null=True, blank=True)
    duration = models.FloatField(default=0, null=True, blank=True)
    number_of_videos = models.IntegerField(default=0)
    language = models.CharField(max_length=255, null=True, blank=True)
    main_stream = models.CharField(max_length=255, null=True, blank=True)
    sub_stream = models.CharField(max_length=255, null=True, blank=True)
    # course_outcomes = models.TextField(null=True, blank=True)
    system_requirements = models.CharField(max_length=255, null=True, blank=True)
    has_subtitles = models.BooleanField(default=False)
    reference_id = models.CharField(max_length=255, null=True, blank=True)
    lms_client = models.ForeignKey('lms.LMSClient', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    client_status = models.BooleanField(default=False)

    status = models.IntegerField(default=0)
    '''
    :status -> CourseStatus
    0 - new
    1 - approved
    2 - rejected
    '''
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.course)


class StudentCourseSubscription:
    NEW = 0
    SUBSCRIBED_SUCCESS = 1
    SUBSCRIBED_FAILED = 2


class StudentCourse(models.Model):

    student = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey('lms.Course', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.IntegerField(default=0)
    """
    :status
    NEW = 0
    SUBSCRIBED_SUCCESS = 1
    SUBSCRIBED_FAILED = 2
    """
    progress_percentage = models.FloatField(default=0)
    assessment_status = models.BooleanField(default=False)
    course_complete = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateField(null=True, blank=True)

    subscription_reference_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_on = models.DateTimeField(null=True, blank=True)
    lms_client = models.ForeignKey('lms.LMSClient', on_delete=models.SET_NULL, null=True, blank=True)
    is_mandatory = models.IntegerField(null=True, blank=True)
    temp_z = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    assessment_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.course)


class LmsApiLog(models.Model):
    lms_client = models.ForeignKey('lms.LMSClient', on_delete=models.SET_NULL, null=True, blank=True)
    payload = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    sub_url = models.CharField(max_length=255, null=True, blank=True)
    status_code = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.lms_client)