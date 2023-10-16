from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from datarepo.models import AccountRole
import random


def gen_otp():
    return random.randint(100000, 999999)


class TempUser(models.Model):
    phone_number = models.IntegerField(unique=True)
    otp = models.IntegerField(default=gen_otp)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    account_role = models.IntegerField(default=8)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = '01 - User'

    def create_registered_user(
            username: str,
            password: str,
            mobile: str,
            email: str,
            account_role: int,
            college_id: int = None,
            student_id: int = None):
        user = None
        check_username = True
        final_username = str(username).strip()
        index_counter = 0
        while check_username:
            get_user = User.objects.filter(username__iexact=final_username).exists()
            if not get_user:
                new_user = User.objects.create(
                    username=str(final_username).lower(), email=email,
                                               account_role=account_role)
                new_user.set_password(password)
                new_user.save()
                user = new_user
                new_user_details = UserDetail.objects.create(
                    user_id=new_user.id,
                    college_id=college_id if account_role in [AccountRole.COLLEGE_ADMIN,
                                                              AccountRole.COLLEGE_ADMIN_STAFF,
                                                              AccountRole.FACULTY] else None,
                    student_id=student_id if account_role == AccountRole.STUDENT else None,
                )
                new_user_details.save()
                check_username = False
            else:
                print(index_counter, mobile)
                if index_counter == len(mobile):
                    mobile = str(random.randint(100000000, 900000000))
                    index_counter = 0

                print(index_counter, mobile)
                final_username = str(username).strip() + str(mobile)[:index_counter + 1]
                # print('final_username', final_username, mobile[:index_counter + 1])
                index_counter += 1
        return user


class UserDetail(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey('college.College', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='profile_college')
    student = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='profile_student')

    verification_code = models.IntegerField(null=True, blank=True)
    verification_request_count = models.IntegerField(default=0)
    verification_attempt = models.IntegerField(null=True, blank=True)
    verification_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '02 - User Detail'


class NMStaffDetails(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('datarepo.District',on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '03 - NM Staff Details'


class PhoneNumberOtp(models.Model):
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    verification_code = models.IntegerField(null=True, blank=True)
    verification_request_count = models.IntegerField(default=0)
    verification_attempt = models.IntegerField(null=True, blank=True)
    verification_expiry = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone_number)

class EOIRegistration(models.Model):
    mobile_number = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    verification_code = models.IntegerField(null=True, blank=True)
    verification_request_count = models.IntegerField(default=0)
    verification_attempt = models.IntegerField(null=True, blank=True)
    verification_expiry = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class EOIDetail(models.Model):
    status = models.IntegerField(default=0)  # 0 - new, 1 - details submitted
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    organisation_name = models.CharField(max_length=255, null=True, blank=True)
    registration_document = models.FileField(null=True, blank=True)

    contact_person_name = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    # sectors_under_which_courses_to_be_offered
    sectors = models.TextField(null=True, blank=True)
    # Specialization of Degree/Branch
    specialization = models.TextField(null=True, blank=True)
    detailed_proposal_document = models.FileField(null=True, blank=True)
    declaration_document = models.FileField(null=True, blank=True)
    details_submitted_on = models.DateTimeField(null=True, blank=True)
    cost_per_student = models.CharField(max_length=255, null=True, blank=True)
    mode = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)