from django.db import models
import uuid


def gen_secret():
    return str(uuid.uuid4()).replace('-', '')[::-1]


def gen_key():
    return str(uuid.uuid4()).replace('-', '')


# Create your models here.

class PsychometricPartner(models.Model):
    client = models.OneToOneField('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    client_secret = models.CharField(max_length=255, unique=True, default=gen_secret)
    client_key = models.CharField(max_length=255, unique=True, default=gen_key)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)


class PsychometricResult(models.Model):
    client = models.ForeignKey(PsychometricPartner, on_delete=models.SET_NULL, blank=True, null=True)
    student = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey('college.college', blank=True, null=True, on_delete=models.SET_NULL)
    result = models.TextField(blank=True, null=True)
    report_url = models.TextField(blank=True, null=True)
