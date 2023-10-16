from django.db import models

# Create your models here.


class Industry(models.Model):
    organisation_name = models.CharField(max_length=255, null=True, blank=True)
    industry_type = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_1_name = models.CharField(max_length=255, null=True, blank=True)
    contact_1_email = models.CharField(max_length=255, null=True, blank=True)
    contact_1_phone_number = models.CharField(max_length=255, null=True, blank=True)
    contact_2_name = models.CharField(max_length=255, null=True, blank=True)
    contact_2_email = models.CharField(max_length=255, null=True, blank=True)
    contact_2_phone_number = models.CharField(max_length=255, null=True, blank=True)

    has_internships = models.BooleanField(default=False)
    internship_poc_name = models.CharField(max_length=255, null=True, blank=True)
    internship_poc_email = models.CharField(max_length=255, null=True, blank=True)
    internship_poc_phone_number = models.CharField(max_length=255, null=True, blank=True)

    has_job_openings = models.BooleanField(default=False)
    job_poc_name = models.CharField(max_length=255, null=True, blank=True)
    job_poc_email = models.CharField(max_length=255, null=True, blank=True)
    job_poc_phone_number = models.CharField(max_length=255, null=True, blank=True)

    industry_speaks = models.TextField(null=True, blank=True)

    status = models.IntegerField(default=0)  # 0 - new, 1 - accept, 2 - reject
    has_mailed = models.BooleanField(default=False)
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.organisation_name)


class Internship(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    internship_title = models.CharField(max_length=255, null=True, blank=True)
    internship_type = models.IntegerField(null=True, blank=True)   # 0 - virtual, 1 - in-person
    eligible_criteria = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    duration = models.FloatField(default=0)  # in months
    no_of_openings = models.IntegerField(default=0)
    last_date_of_application = models.DateField(null=True, blank=True)
    skills_required = models.TextField(null=True, blank=True)
    free_or_paid = models.IntegerField(null=True, blank=True)   # 0 - free, 1 - paid
    stipend_details = models.TextField(null=True, blank=True)
    other_perks = models.TextField(null=True, blank=True)
    about_internship = models.TextField(null=True, blank=True)
    additional_information = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.internship_title)


class Job(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    educational_qualification = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    no_of_openings = models.IntegerField(default=0)
    last_date_of_application = models.DateField(null=True, blank=True)
    skills_required = models.TextField(null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)   # in rupee

    other_perks = models.TextField(null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    additional_information = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.job_title)


class Training(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    training_title = models.CharField(max_length=255, null=True, blank=True)
    educational_qualification = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    no_of_openings = models.IntegerField(default=0)
    last_date_of_application = models.DateField(null=True, blank=True)
    skills_required = models.TextField(null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)   # in rupee

    other_perks = models.TextField(null=True, blank=True)
    training_description = models.TextField(null=True, blank=True)
    additional_information = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.training_title)


class Mentorship(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    mentor_name = models.CharField(max_length=255, null=True, blank=True)
    mentor_email = models.CharField(max_length=255, null=True, blank=True)
    mentor_phone_number = models.CharField(max_length=255, null=True, blank=True)
    designation = models.TextField(null=True, blank=True)
    availability = models.IntegerField(default=0)   # Hours/ week
    mode = models.IntegerField(null=True, blank=True)   # 0 - virtual, 1 - in-person
    linkedin_profile_url = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.mentor_name)
