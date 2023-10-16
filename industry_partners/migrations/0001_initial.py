# Generated by Django 4.0.5 on 2023-07-05 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organisation_name', models.CharField(blank=True, max_length=255, null=True)),
                ('industry_type', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_1_name', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_1_email', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_1_phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_2_name', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_2_email', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_2_phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('has_internships', models.BooleanField(default=False)),
                ('internship_poc_name', models.CharField(blank=True, max_length=255, null=True)),
                ('internship_poc_email', models.CharField(blank=True, max_length=255, null=True)),
                ('internship_poc_phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('has_job_openings', models.BooleanField(default=False)),
                ('job_poc_name', models.CharField(blank=True, max_length=255, null=True)),
                ('job_poc_email', models.CharField(blank=True, max_length=255, null=True)),
                ('job_poc_phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('industry_speaks', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField(default=0)),
                ('has_mailed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('training_title', models.CharField(blank=True, max_length=255, null=True)),
                ('educational_qualification', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('no_of_openings', models.IntegerField(default=0)),
                ('last_date_of_application', models.DateField(blank=True, null=True)),
                ('skills_required', models.TextField(blank=True, null=True)),
                ('salary', models.IntegerField(blank=True, null=True)),
                ('other_perks', models.TextField(blank=True, null=True)),
                ('training_description', models.TextField(blank=True, null=True)),
                ('additional_information', models.TextField(blank=True, null=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('taluk', models.CharField(blank=True, max_length=255, null=True)),
                ('district', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('industry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='industry_partners.industry')),
            ],
        ),
        migrations.CreateModel(
            name='Mentorship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mentor_name', models.CharField(blank=True, max_length=255, null=True)),
                ('mentor_email', models.CharField(blank=True, max_length=255, null=True)),
                ('mentor_phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('designation', models.TextField(blank=True, null=True)),
                ('availability', models.IntegerField(default=0)),
                ('mode', models.IntegerField(blank=True, null=True)),
                ('linkedin_profile_url', models.TextField(blank=True, null=True)),
                ('languages', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('industry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='industry_partners.industry')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(blank=True, max_length=255, null=True)),
                ('educational_qualification', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('no_of_openings', models.IntegerField(default=0)),
                ('last_date_of_application', models.DateField(blank=True, null=True)),
                ('skills_required', models.TextField(blank=True, null=True)),
                ('salary', models.IntegerField(blank=True, null=True)),
                ('other_perks', models.TextField(blank=True, null=True)),
                ('job_description', models.TextField(blank=True, null=True)),
                ('additional_information', models.TextField(blank=True, null=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('taluk', models.CharField(blank=True, max_length=255, null=True)),
                ('district', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('industry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='industry_partners.industry')),
            ],
        ),
        migrations.CreateModel(
            name='Internship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('internship_title', models.CharField(blank=True, max_length=255, null=True)),
                ('internship_type', models.IntegerField(blank=True, null=True)),
                ('eligible_criteria', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('duration', models.FloatField(default=0)),
                ('no_of_openings', models.IntegerField(default=0)),
                ('last_date_of_application', models.DateField(blank=True, null=True)),
                ('skills_required', models.TextField(blank=True, null=True)),
                ('free_or_paid', models.IntegerField(blank=True, null=True)),
                ('stipend_details', models.TextField(blank=True, null=True)),
                ('other_perks', models.TextField(blank=True, null=True)),
                ('about_internship', models.TextField(blank=True, null=True)),
                ('additional_information', models.TextField(blank=True, null=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('taluk', models.CharField(blank=True, max_length=255, null=True)),
                ('district', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('industry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='industry_partners.industry')),
            ],
        ),
    ]