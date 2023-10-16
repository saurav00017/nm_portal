# Generated by Django 4.0.5 on 2023-07-05 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kp', '0001_initial'),
        ('lms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimpleCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('course_type', models.CharField(blank=True, choices=[('API', 'API'), ('OFFLINE', 'OFFLINE')], max_length=100, null=True)),
                ('link', models.TextField(blank=True, null=True)),
                ('hours', models.IntegerField(default=0)),
                ('knowledge_partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kp.knowledgepartner')),
                ('lms_course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lms.course')),
            ],
        ),
    ]