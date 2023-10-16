from django.db import models

# Create your models here.





class DistrictReport(models.Model):
    district = models.ForeignKey('datarepo.District', on_delete=models.SET_NULL, null=True, blank=True)
    total_no_of_colleges = models.BigIntegerField(default=0)
    total_no_of_colleges_invited = models.BigIntegerField(default=0)
    total_no_of_colleges_registered = models.BigIntegerField(default=0)
    total_no_of_colleges_subscribed = models.BigIntegerField(default=0)

    # college types
    college_type_1 = models.BigIntegerField(default=0)
    college_type_2 = models.BigIntegerField(default=0)
    college_type_3 = models.BigIntegerField(default=0)
    college_type_4 = models.BigIntegerField(default=0)
    college_type_5 = models.BigIntegerField(default=0)

    # students
    total_no_of_students = models.BigIntegerField(default=0)
    college_type_1_students = models.BigIntegerField(default=0)
    college_type_2_students = models.BigIntegerField(default=0)
    college_type_3_students = models.BigIntegerField(default=0)
    college_type_4_students = models.BigIntegerField(default=0)
    college_type_5_students = models.BigIntegerField(default=0)

    # Student Gender level
    total_no_of_male_students = models.BigIntegerField(default=0)
    total_no_of_female_students = models.BigIntegerField(default=0)
    total_no_of_other_students = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.district)


class CollegeReport(models.Model):
    college = models.ForeignKey('college.College', on_delete=models.SET_NULL, null=True, blank=True)
    college_type = models.IntegerField(null=True, blank=True)
    """
    :college_type --> College Type
    1 - ARTS_AND_SCIENCE
    2 - ENGINEERING
    3 - ITI
    4 - POLYTECHNIC
    5 - PHARMA
    """

    district = models.ForeignKey('datarepo.District', on_delete=models.SET_NULL, null=True, blank=True)
    affiliated_university = models.ForeignKey('datarepo.AffiliatedUniversity', blank=True, null=True,
                                              on_delete=models.SET_NULL)
    # students
    total_no_of_students = models.BigIntegerField(default=0)
    total_no_of_students_invited = models.BigIntegerField(default=0)
    total_no_of_students_registered = models.BigIntegerField(default=0)
    total_no_of_students_subscribed = models.BigIntegerField(default=0)
    # Student Gender level
    total_no_of_male_students = models.BigIntegerField(default=0)
    total_no_of_female_students = models.BigIntegerField(default=0)
    total_no_of_other_students = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.district_id) + " - " + str(self.district)
