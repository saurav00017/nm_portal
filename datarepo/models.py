from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .file_async import sync_file_with_scp


# Create your models here.


class District(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.name)


class AffiliatedUniversity(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class CollegeManagementType:
    GOVERNMENT = 1
    PRIVATE_AIDED_AUTONOMOUS = 4
    GOVERNMENT_AUTONOMOUS = 2
    PRIVATE_AIDED = 3
    PRIVATE_UNAIDED = 5
    PRIVATE_UNAIDED_AUTONOMOUS = 6
    UNIVERSITY_AUTONOMOUS = 7
    UNIVERSITY_AUTONOMOUS_COLLEGE = 8
    AIDED = 9
    GOVERNMENT_AIDED = 10
    GOVERNMENT_AIDED_AUTONOMOUS = 11
    PER_DEPARTMENT = 12
    SELF_FINIANCING = 13
    SELF_FINIANCING_AUTONOMOUS = 14


class CollegeType:
    """
    If new college_type added ->
        need to add new Field in reports.DistrictReport Model
    """
    ARTS_AND_SCIENCE = 1
    ENGINEERING = 2
    ITI = 3
    POLYTECHNIC = 4
    PHARMA = 5

    def __init__(self, attr):
        self.attr = attr


class AccountRole:
    SUPER_ADMIN = 1
    NM_ADMIN = 2
    NM_ADMIN_STAFF = 3
    DISTRICT_ADMIN = 4
    DISTRICT_ADMIN_STAFF = 5
    COLLEGE_ADMIN = 6
    COLLEGE_ADMIN_STAFF = 7
    STUDENT = 8
    LMS_API_USER = 9
    PSYCHOMETRIC_API_USER = 10
    KNOWLEDGE_PARTNER = 11

    INDUSTRY_ADMIN = 12
    INDUSTRY_STAFF = 13
    INDUSTRY_USER = 14
    EOI_USER = 15
    FACULTY = 16


class PaymentStatus:
    INITIATE = 1
    SUCCESS = 2
    FAILED = 3


class StudentPaymentStatus:
    PENDING = 0
    PAYMENT_IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3


class StudentRegistrationStatus:
    ADDED_TO_DB = 0
    INVITE_SEND = 1
    REGISTRATION_IN_PROGRESS = 2
    REGISTRATION_COMPLETE = 3
    PAYMENT_COMPLETE = 4
    PENDING_APPROVAL = 5
    APPROVED = 6


class StudentCaste:
    ST = 1
    SC = 2
    BC = 3
    OC = 4
    OBC = 5
    GENERAL = 6


class Gender:
    MALE = 1
    FEMALE = 2
    OTHER = 3


class StudentDegree:
    B_TECH = 1
    DIPLOMA = 2
    ITI = 3
    PHARMACY = 4


class SkillOfferingFor:
    ENGINEERING = 0
    DEGREE = 1
    PHARMACY = 2
    MBA_AND_MAC_AND_PG = 3


class Branch(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    branch_type = models.IntegerField(null=True, blank=True)
    # 2 engineering
    # 4 poly
    # 1 degree


class YearOfStudy(models.Model):
    year = models.IntegerField()


class SkillOffering(models.Model):
    skill_offering_for = models.IntegerField(null=True, blank=True)
    technology = models.CharField(max_length=255, null=True, blank=True)
    training_module = models.CharField(max_length=255, null=True, blank=True)
    specialization = models.CharField(max_length=255, null=True, blank=True)
    year_of_study = models.CharField(max_length=255, null=True, blank=True)
    live_training = models.CharField(max_length=255, null=True, blank=True)
    live_virtual_training = models.CharField(
        max_length=255, null=True, blank=True)
    certification = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.skill_offering_for) + " - " + str(self.technology)


class Zone(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class CollegeCategory(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Announcement(models.Model):
    """

    "date": "2022-10-26T08:40:28.117089Z",
    "link": "https://www.freecodecamp.org/news/harvard-cs50/",
    "title": "Check out the best Computer Science course from Harvard for free",
    "description": "",
    "title_tamil": "Check out the best CS course from Harvard for free",
    "description_tamil": "",
    """
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    title_tamil = models.TextField(null=True, blank=True)
    description_tamil = models.TextField(null=True, blank=True)

    date = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)


class PortalAnnouncement(models.Model):
    """

    "date": "2022-10-26T08:40:28.117089Z",
    "link": "https://www.freecodecamp.org/news/harvard-cs50/",
    "title": "Check out the best Computer Science course from Harvard for free",
    "description": "",
    "title_tamil": "Check out the best CS course from Harvard for free",
    "description_tamil": "",
    """
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    title_tamil = models.TextField(null=True, blank=True)
    description_tamil = models.TextField(null=True, blank=True)
    college_type = models.IntegerField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    announcement_type = models.IntegerField(default=0)
    """
    :announcement_type
    0 - all
    1 - college
    2 - student
    """
    date = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)


@receiver(post_save, sender=PortalAnnouncement)
def portal_announcement_update(sender, instance, created, **kwargs):
    try:
        sync_file_with_scp(instance.file)
    except Exception as e:
        print(str(e))
