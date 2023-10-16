from django.db import models

# Create your models here.

class StudentPlacementDetail(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True)
    """
    {
        "current_status": "",
        "job_offers": [
          {
            "sector": "",
            "company_name": "",
            "location": "",
            "salary_package": "",
          }
        ],
        "education_location": "",
        "education_location_other": "",
        "education_degree": "",
        "education_degree_other": "",
        "competitive_exam": "",
        "competitive_exam_other": "",

        "business_sector": "",
        "job_domain": "",
        "job_domain_other": "",
      }
    """
    current_status = models.CharField(max_length=255, null=True, blank=True)
    job_offers = models.JSONField(null=True, blank=True)
    education_location = models.TextField(null=True, blank=True)
    education_location_other = models.TextField(null=True, blank=True)
    education_degree = models.TextField(null=True, blank=True)
    competitive_exam = models.TextField(null=True, blank=True)
    competitive_exam_other = models.TextField(null=True, blank=True)
    business_sector = models.TextField(null=True, blank=True)
    job_domain = models.TextField(null=True, blank=True)
    job_domain_other = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)