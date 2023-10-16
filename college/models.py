from django.db import models, signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from reports.models import DistrictReport, CollegeReport
import uuid
from datarepo.models import CollegeType, Zone, CollegeCategory

from django.db import transaction as atomic_transaction
from datarepo.models import Branch


def get_uuid():
    uid = uuid.uuid4()
    return str(uid)[::-1].replace("-", '')


# Create your models here.


class RegistrationStepOne(models.Model):
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


class CollegeStatus:
    NEW = 0
    REGISTERED = 1
    PAYMENT_DONE = 2


class College(models.Model):
    mandatory_release = models.BooleanField(default=False)

    step_one = models.ForeignKey(RegistrationStepOne, on_delete=models.SET_NULL, null=True, blank=True)
    invitation_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=0)
    '''
    :status
    0 - new / college data added  
    1 - registered / admin account_created
    2 - payment done / first login complete  
    
    '''
    """
    ## Institute Details
    """
    college_name = models.CharField(max_length=300, null=True, blank=True)
    college_code = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    is_mailed = models.BooleanField(default=False)
    mobile = models.CharField(max_length=255, null=True, blank=True)

    spoc_name = models.CharField(max_length=255, null=True, blank=True)

    college_type = models.IntegerField(null=True, blank=True)  # CollegeType

    """
    :college_type --> College Type
    1 - ARTS_AND_SCIENCE
    2 - ENGINEERING
    3 - ITI
    4 - POLYTECHNIC
    """
    affiliated_university = models.ForeignKey('datarepo.AffiliatedUniversity', on_delete=models.SET_NULL, null=True,
                                              blank=True)
    zone = models.ForeignKey('datarepo.Zone', on_delete=models.SET_NULL, null=True,
                             blank=True)

    management_type = models.IntegerField(null=True, blank=True)  # ManagementType
    """
    1. government / Government
    2. government autonomous 
    3. private aided
    4. private aided autonomous
    5. private unaided
    6. private unaided autonomous
    7. university autonomous
    8. university autonomous college
    9. Aided
    10. Government Aided
    11. Government Aided Autonomous
    12. PER-DEPARTMENT
    13. Self Financing
    14. Self Financing Autonomouss


    """  # String from api
    year_of_establishment = models.IntegerField(null=True, blank=True)
    total_faculty_count = models.IntegerField(default=0)
    total_1st_year_students_count = models.IntegerField(default=0)
    total_2nd_year_students_count = models.IntegerField(default=0)
    total_3rd_year_students_count = models.IntegerField(default=0)
    total_4th_year_students_count = models.IntegerField(default=0)

    total_students_count = models.IntegerField(default=0)
    details_submitted_at = models.DateTimeField(null=True, blank=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    # landmark = models.CharField(max_length=255, null=True, blank=True)
    # mandal = models.CharField(max_length=255, null=True, blank=True)
    village = models.CharField(max_length=255, null=True, blank=True)
    town_city = models.CharField(max_length=255, null=True, blank=True)
    district = models.ForeignKey('datarepo.District', on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)

    fax_number = models.CharField(max_length=255, null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    subscription_status = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)

    '''Need to Discuss about Contact Details'''  # these details will be created as accounts (User)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    taluk = models.CharField(blank=True, max_length=255, null=True)
    is_students_verified = models.BooleanField(default=False)
    college_category = models.ForeignKey(CollegeCategory, on_delete=models.SET_NULL, null=True, blank=True)

    course_allocation = models.IntegerField(default=0)
    external_assessment = models.IntegerField(default=0)
    principal_name = models.CharField(max_length=255, null=True, blank=True)
    principal_mobile = models.CharField(max_length=255, null=True, blank=True)
    principal_email = models.CharField(max_length=255, null=True, blank=True)

    placement_name = models.CharField(max_length=255, null=True, blank=True)
    placement_mobile = models.CharField(max_length=255, null=True, blank=True)
    placement_email = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.college_code) + " -  " + str(self.college_name)

    class Meta:
        verbose_name = '02 - College'


# method for updating
@receiver(post_save, sender=College, dispatch_uid="update_district_report")
def update_district_report(sender, instance, created, **kwargs):
    if created:
        if instance.district_id:
            print(instance.district_id, "==> ")
            try:
                with atomic_transaction.atomic():
                    get_district_report = DistrictReport.objects.select_for_update().get(
                        district_id=instance.district_id)
                    get_district_report.total_no_of_colleges += 1
                    get_district_report.total_no_of_colleges_invited += 1

                    if instance.college_type == CollegeType.ARTS_AND_SCIENCE:
                        get_district_report.college_type_1 += 1
                    elif instance.college_type == CollegeType.ENGINEERING:

                        get_district_report.college_type_2 += 1
                    elif instance.college_type == CollegeType.ITI:
                        get_district_report.college_type_3 += 1
                    elif instance.college_type == CollegeType.POLYTECHNIC:
                        get_district_report.college_type_4 += 1
                    elif instance.college_type == CollegeType.PHARMA:
                        get_district_report.college_type_5 += 1
                    get_district_report.save()

                    new_college_report = CollegeReport.objects.create(
                        college_id=instance.id,
                        college_type=instance.college_type,
                        district_id=instance.district_id,
                        affiliated_university_id=instance.affiliated_university_id,
                    )
            except DistrictReport.DoesNotExist:
                print("--> instance.district_id", instance.district_id)
                if instance.district_id:
                    new_district_report = DistrictReport.objects.create(
                        district_id=instance.district_id,
                        total_no_of_colleges=1,
                        total_no_of_colleges_invited=1,
                        college_type_1=1 if instance.college_type == CollegeType.ARTS_AND_SCIENCE else 0,
                        college_type_2=1 if instance.college_type == CollegeType.ENGINEERING else 0,
                        college_type_3=1 if instance.college_type == CollegeType.ITI else 0,
                        college_type_4=1 if instance.college_type == CollegeType.POLYTECHNIC else 0,
                        college_type_5=1 if instance.college_type == CollegeType.PHARMA else 0,
                    )

                    new_college_report = CollegeReport.objects.create(
                        college_id=instance.id,
                        college_type=instance.college_type,
                        district_id=instance.district_id,
                        affiliated_university_id=instance.affiliated_university_id,
                    )
            except Exception as e:
                print(" \n\n\t---->", e)


class CollegeSubscription(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
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
        return str(self.college)

    class Meta:
        verbose_name = '03 - College Subscription'


class CollegeOtpVerification(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    otp_type = models.IntegerField(null=True, blank=True)  # 0 - phone number, 1 - email
    otp = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    is_otp_send = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'College Otp Verification'


class CollegeFaculty(models.Model):
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    assigned_faculty_id = models.CharField(max_length=255, null=True, blank=True)
    highest_educational_qualification = models.TextField(null=True, blank=True)
    pg_specialization = models.TextField(null=True, blank=True)
    years_of_experience = models.TextField(null=True, blank=True)
    in_industry_research_others = models.TextField(null=True, blank=True)
    document = models.FileField(null=True, blank=True)
    has_master_trainer_on_honoraraium_basis = models.IntegerField(default=0)
    any_relevant_certification = models.TextField(null=True, blank=True)
    details_of_skills = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class FacultyFDPDetails(models.Model):
    faculty = models.ForeignKey(CollegeFaculty, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    technology = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
