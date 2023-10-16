from django.db import models
from kp.models import KnowledgePartner


# Create your models here.


class FSCourse(models.Model):
    knowledge_partner = models.ForeignKey(KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    details = models.JSONField(blank=True, null=True)
    status = models.IntegerField(default=1)  # 0 submitted 1 rejected 2 inactive 3 active
    enrollment_type = models.IntegerField(default=1)  #

    def __str__(self):
        return self.name


class FSEnrollment(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey('college.college', blank=True, null=True, on_delete=models.SET_NULL)
    knowledge_partner = models.ForeignKey(KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    fs_course = models.ForeignKey(FSCourse, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.IntegerField(blank=True,
                                 null=True)
    # 0 awaiting kp approval
    # 1 rejected kp approval
    # 2 approved
    comment = models.TextField(blank=True, null=True)
    enrollment_type = models.IntegerField(default=1)  #
    # 0 online
    # 1 offline


class FSEnrollmentProgress(models.Model):
    fs_course = models.ForeignKey(FSCourse, on_delete=models.SET_NULL, null=True, blank=True)
    knowledge_partner = models.ForeignKey(KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    progress_percentage = models.FloatField(default=0, null=True, blank=True)
    assessment_status = models.BooleanField(default=False, null=True, blank=True)
    course_complete = models.BooleanField(default=False, null=True, blank=True)
    certificate_issued = models.BooleanField(default=False, null=True, blank=True)
    certificate_issued_at = models.DateField(null=True, blank=True)
