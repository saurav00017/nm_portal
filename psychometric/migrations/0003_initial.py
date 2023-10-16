# Generated by Django 4.0.5 on 2023-07-05 12:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('psychometric', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='psychometricpartner',
            name='client',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
