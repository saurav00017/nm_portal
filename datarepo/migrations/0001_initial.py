# Generated by Django 4.0.5 on 2023-07-05 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AffiliatedUniversity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('link', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('title_tamil', models.TextField(blank=True, null=True)),
                ('description_tamil', models.TextField(blank=True, null=True)),
                ('date', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('branch_type', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CollegeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PortalAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('link', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('title_tamil', models.TextField(blank=True, null=True)),
                ('description_tamil', models.TextField(blank=True, null=True)),
                ('college_type', models.IntegerField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('announcement_type', models.IntegerField(default=0)),
                ('date', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SkillOffering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_offering_for', models.IntegerField(blank=True, null=True)),
                ('technology', models.CharField(blank=True, max_length=255, null=True)),
                ('training_module', models.CharField(blank=True, max_length=255, null=True)),
                ('specialization', models.CharField(blank=True, max_length=255, null=True)),
                ('year_of_study', models.CharField(blank=True, max_length=255, null=True)),
                ('live_training', models.CharField(blank=True, max_length=255, null=True)),
                ('live_virtual_training', models.CharField(blank=True, max_length=255, null=True)),
                ('certification', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='YearOfStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datarepo.district')),
            ],
        ),
    ]