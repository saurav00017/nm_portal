from django.db import models
import uuid
from django.db import models, signals
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from reports.models import DistrictReport, CollegeReport
from datarepo.models import CollegeType, Gender
from college.models import College
from django.conf import settings
from datarepo.models import Branch
from django.db import transaction as atomic_transaction


def student_invitation_id_gen():
    return str(uuid.uuid4()).replace("-", "")[:32][::-1].upper()





class StudentRegistrationStepOne(models.Model):
    college = models.ForeignKey('college.college', blank=True, null=True, on_delete=models.SET_NULL)

    """
    :status
     0 - added
     1 - initiate (in-progress)
     2 - completed
     3 - failed at background task
    """
    status = models.IntegerField(default=0)
    csv_file = models.FileField(upload_to='college_registrations')
    # Counters
    total_count = models.IntegerField(default=0)
    valid_count = models.IntegerField(default=0)
    invalid_count = models.IntegerField(default=0)
    already_exist_count = models.IntegerField(default=0)
    # check points
    is_mailed = models.BooleanField(default=False)

    user = models.ForeignKey('users.user', on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '01 - Registration'


class StudentConcessions:
    NEW = 0
    FILE_UPLOADED = 1
    APPROVED = 2
    REJECTED = 3


class Student(models.Model):
    step_one = models.ForeignKey(StudentRegistrationStepOne, on_delete=models.SET_NULL, null=True, blank=True)
    # check points
    is_mailed = models.BooleanField(default=False)
    invitation_id = models.CharField(default=student_invitation_id_gen, unique=True, max_length=40, null=True,
                                     blank=True)
    """
    0. pending
    1. payment in progress
    2. complete
    3. failed
    """
    payment_status = models.IntegerField(default=0)
    """
    :registration_status
    0. added to db
    1. invite sent
    2. registration in progress
    3. registration complete
    4. payment complete
    ========================
    5. user created
    6. user detail created
    7. email success
    8. email failed
    9. sms sent 
    10. sms sent 
    11. flag set
    12. first login
    
    """
    registration_status = models.IntegerField(default=0)
    verification_status = models.IntegerField(default=0)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    roll_no = models.CharField(max_length=100, blank=True, null=True)  # institution ID
    is_temporary_roll_number = models.BooleanField(default=False)
    sem = models.IntegerField(blank=True, null=True)
    """
    1. ST
    2. SC
    3. BC
    4. OC
    5. OBC
    6. GENERAL
    """
    caste = models.IntegerField(blank=True, null=True)
    certificate = models.FileField(upload_to='student/caste_certificate/', blank=True, null=True)

    is_pass_out = models.BooleanField(default=False)
    provisional_certificate = models.FileField(upload_to='student/provisional_certificate/', blank=True, null=True)
    concessions = models.IntegerField(null=True, blank=True)
    aadhar_number = models.CharField(max_length=100, blank=True, null=True)

    rbranch = models.ForeignKey(Branch, blank=True, null=True,
                                on_delete=models.SET_NULL)

    branch = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    """
    1. male
    2. female
    3. others
    """
    gender = models.IntegerField(blank=True, null=True)
    college = models.ForeignKey('college.college', blank=True, null=True, on_delete=models.SET_NULL)
    """
    : degree -> CollegeType
    ARTS_AND_SCIENCE = 1
    ENGINEERING = 2
    ITI = 3
    POLYTECHNIC = 4
    """
    degree = models.IntegerField(default=2, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    affiliated_university = models.ForeignKey('datarepo.AffiliatedUniversity', blank=True, null=True,
                                              on_delete=models.SET_NULL)

    # current_address = models.TextField(blank=True, null=True)
    # permanent_address = models.TextField(blank=True, null=True)
    # current
    current_address = models.CharField(max_length=255, null=True, blank=True)
    current_village = models.CharField(max_length=255, null=True, blank=True)
    current_town_city = models.CharField(max_length=255, null=True, blank=True)
    # current_district = models.ForeignKey('datarepo.District', on_delete=models.SET_NULL, null=True, blank=True, related_name='student_current_district')
    current_district = models.CharField(max_length=255, null=True, blank=True)
    current_state = models.CharField(max_length=255, null=True, blank=True)
    current_pincode = models.IntegerField(null=True, blank=True)
    # permanent
    permanent_address = models.CharField(max_length=255, null=True, blank=True)
    # permanent_landmark = models.CharField(max_length=255, null=True, blank=True)
    # permanent_mandal = models.CharField(max_length=255, null=True, blank=True)
    permanent_village = models.CharField(max_length=255, null=True, blank=True)
    permanent_town_city = models.CharField(max_length=255, null=True, blank=True)
    # permanent_district = models.ForeignKey('datarepo.District', on_delete=models.SET_NULL, null=True, blank=True, related_name='student_permanent_district')
    permanent_district = models.CharField(max_length=255, null=True, blank=True)
    permanent_state = models.CharField(max_length=255, null=True, blank=True)
    permanent_pincode = models.IntegerField(null=True, blank=True)

    hall_ticket_number = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    year_of_graduation = models.IntegerField(blank=True, null=True)
    tenth_pass_out_year = models.IntegerField(blank=True, null=True)
    tenth_cgpa = models.FloatField(blank=True, null=True)
    intermediate_pass_out_year = models.IntegerField(blank=True, null=True)
    is_first_year_in_degree = models.BooleanField(blank=True, null=True)
    current_graduation_cgpa = models.FloatField(blank=True, null=True)
    has_backlogs = models.BooleanField(blank=True, null=True)
    subscription_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_free_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + " - " + str(self.first_name) + " - " + str(self.last_name)

    class Meta:
        verbose_name = '01 - Student'

from datarepo.file_async import sync_file_with_scp

# method for updating
@receiver(post_save, sender=Student, dispatch_uid="update_college_report")
def update_college_report(sender, instance, created, **kwargs):
    if created:
        if instance.college_id:
            try:
                with atomic_transaction.atomic():
                    get_college_report = CollegeReport.objects.select_for_update().filter(
                        college_id=instance.college_id).first()
                    if get_college_report:
                        get_college_report.total_no_of_students += 1
                        get_college_report.total_no_of_students_invited += 1
                        get_college_report.save()
            except CollegeReport.DoesNotExist:
                new_college_report = CollegeReport.objects.create(
                    district_id=instance.college.district_id,
                    college_type=instance.college.college_type,
                    college_id=instance.college_id,
                    affiliated_university_id=instance.college.affiliated_university_id,
                    total_no_of_students=1,
                    total_no_of_students_invited=1,
                )
    try:
        certificate_sync_status = False
        provisional_certificate_sync_status = False
        if created:
            certificate_sync_status = True
            provisional_certificate_sync_status = True
        else:
            record = Student.objects.get(id=instance.id)
            if record.provisional_certificate != instance.provisional_certificate:
                provisional_certificate_sync_status = True
            if record.certificate != instance.certificate:
                certificate_sync_status = True

        if certificate_sync_status:
            sync_file_with_scp(instance.certificate)
        if provisional_certificate_sync_status:
            sync_file_with_scp(instance.provisional_certificate)
    except Exception as e:
        print(str(e))


class StudentPaymentDetail(models.Model):
    student = models.ForeignKey('student.Student', blank=True, null=True, on_delete=models.SET_NULL)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    """
       ## Payment details
       """
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_order_receipt = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    razorpay_created_at = models.CharField(max_length=255, null=True, blank=True)

    registration_fee = models.FloatField(default=0)
    '''
    :payment_mode
    0 - online
    1 - offline 
    '''
    payment_mode = models.IntegerField(null=True, blank=True)
    '''
    :payment_status
    1 - initiate
    2 - success
    3 - failed'''
    payment_status = models.IntegerField(default=0)
    payment_done_at = models.DateTimeField(null=True, blank=True)
    """
    ## Razorpay fields
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)

    class Meta:
        verbose_name = '03 - Student Subscription'


class TemporaryFileUpload(models.Model):
    status = models.IntegerField(default=0)
    college_type = models.IntegerField(null=True, blank=True)
    """
    :status
    0 - file upload
    1 - result generation in progress 
    2 - result generation in completed
    3 - in_process 
    4 - return to DB
    """
    csv_file_data = models.JSONField(null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class CollegeTemporaryFileUpload(models.Model):
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.IntegerField(default=0)
    college_type = models.IntegerField(null=True, blank=True)
    """
    :status
    0 - file upload
    1 - In Progress
    2 - failed
    3 - success
    4 - Partially success
    """
    csv_file = models.FileField(null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

"""
"College Code,Student Name,Roll No,Mobile,Email,Branch ID,Sem", 
"7176,ABISHEK R S,71762101001,718319363592,abishekrs2003@gmail.com,84,2", 
"7176,AGALYA P,7176 21 01 002,552261823351,agalyaperumal2004@gmail.com,84,2", 
"7176,AHILESH RAJ A,7176 21 01 
"""

