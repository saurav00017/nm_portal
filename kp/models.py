from django.db import models
from users.models import User
from lms.models import LMSClient

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from datarepo.file_async import sync_file_with_scp

# Create your models here.


class KnowledgePartner(models.Model):
    lms_client = models.ForeignKey(LMSClient, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='images/', blank=True, null=True)
    is_fs = models.BooleanField(default=False)
    enable_api = models.BooleanField(default=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=KnowledgePartner)
def sync_logo_file(sender, instance, created, **kwargs):
    try:
        sync_file_with_scp(instance.logo)
    except Exception as e:
        print("KnowledgePartner - sync_file_with_scp:Error:", str(e))


class LinkPartner(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=LinkPartner)
def sync_link_partner_logo_file(sender, instance, created, **kwargs):
    try:
        sync_file_with_scp(instance.logo)
    except Exception as e:
        print("LinkPartner - sync_file_with_scp:Error:", str(e))

