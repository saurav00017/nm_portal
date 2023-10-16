from django.db import models
from kp.models import KnowledgePartner
from lms.models import Course


# Create your models here.

class SimpleCourse(models.Model):
    COURSE_TYPES = (
        ('API', 'API'),
        ('OFFLINE', 'OFFLINE'),
    )
    knowledge_partner = models.ForeignKey(KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    lms_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    course_type = models.CharField(max_length=100, blank=True, null=True, choices=COURSE_TYPES)  # 0 API , 1 OFFLINE
    link = models.TextField(blank=True, null=True)
    hours = models.IntegerField(default=0)
