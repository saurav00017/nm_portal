import uuid

from django.db import models
from kp.models import KnowledgePartner
from datarepo.models import Branch, YearOfStudy
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from datarepo.file_async import sync_file_with_scp_with_path
from textwrap import TextWrapper
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
from django.conf import settings
from django.utils import timezone
from django.db import transaction as atomic_transaction
import qrcode
# from college.models import CollegeFaculty
# Create


def get_uuid():
    uid = uuid.uuid4()
    return str(uid).replace("-", '')[::-1]


class Specialisation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SubTechnology(models.Model):
    tech = models.ForeignKey(Technology, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SKillOffering(models.Model):
    knowledge_partner = models.ForeignKey(
        KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    technology = models.ForeignKey(
        Technology, on_delete=models.SET_NULL, null=True, blank=True)
    course_code = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    sub_technology = models.ForeignKey(
        SubTechnology, on_delete=models.SET_NULL, null=True, blank=True)
    specialization = models.ManyToManyField(
        Specialisation, null=True, blank=True)
    branch = models.ManyToManyField(Branch, null=True, blank=True)
    year_of_study = models.ManyToManyField(YearOfStudy, null=True, blank=True)
    mode_of_delivery = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    outcomes = models.TextField(null=True, blank=True)
    course_content = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    certification = models.CharField(max_length=255, null=True, blank=True)
    cost = models.CharField(max_length=255, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    is_mandatory = models.IntegerField(default=0)  # 0 no 1 yes
    sem = models.IntegerField(null=True, blank=True)  # 0 no 1 yes
    lms_course = models.ForeignKey(
        'lms.Course', on_delete=models.SET_NULL, null=True, blank=True)
    offering_type = models.IntegerField(
        blank=True, null=True)  # 0 offline 1 online 2 API
    offering_kind = models.IntegerField(blank=True, null=True)  # 0 free 1 paid
    job_category = models.TextField(null=True, blank=True)

    status = models.IntegerField(default=1)  # 0 - in-active, 1 - active
    ea_count = models.IntegerField(default=0)  # External Assessment Count
    ia_count = models.IntegerField(
        null=True, blank=True)  # Internal Assessment Count
    manually_editable = models.BooleanField(default=False)

    def __str__(self):
        return str(self.course_name) + " - " + str(self.course_code)


class SKillOfferingEnrollment(models.Model):
    faculty = models.ForeignKey(
        'college.CollegeFaculty', on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(
        'student.Student', on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey(
        'college.college', blank=True, null=True, on_delete=models.SET_NULL)
    knowledge_partner = models.ForeignKey(
        KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    skill_offering = models.ForeignKey(
        SKillOffering, on_delete=models.SET_NULL, null=True, blank=True)
    lms_course = models.ForeignKey(
        'lms.Course', on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.IntegerField(blank=True,
                                 null=True)
    # 0 awaiting college approval
    # 1 rejected at college
    # 2 awaiting kp approval
    # 3 rejected kp approval
    # 4 approved
    offering_type = models.IntegerField(
        blank=True, null=True)  # 0 offline 1 API 2 link_only
    offering_kind = models.IntegerField(blank=True, null=True)  # 0 free 1 paid
    comment = models.TextField(blank=True, null=True)
    is_mandatory = models.IntegerField(default=0)  # 0 no 1 yes

    def __str__(self):
        return str(self.student) + " - " + str(self.skill_offering)


class SKillOfferingEnrollmentCertificate(models.Model):

    certificate_id = models.CharField(
        default=get_uuid, unique=True, max_length=40, null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    skill_offering_enrollment = models.ForeignKey(
        SKillOfferingEnrollment, on_delete=models.SET_NULL, null=True, blank=True)
    knowledge_partner = models.ForeignKey(
        KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    certificate = models.FileField(
        null=True, blank=True, upload_to='skill_offering/certificates')
    certificate_no = models.CharField(max_length=255, null=True, blank=True)
    issue_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    college_type = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


def generate_certificate(instance: SKillOfferingEnrollmentCertificate):
    if instance.skill_offering_enrollment_id:
        if instance.skill_offering_enrollment.skill_offering_id and instance.skill_offering_enrollment.student_id:
            if not instance.certificate:
                with atomic_transaction.atomic():
                    try:
                        instance = SKillOfferingEnrollmentCertificate.objects.select_for_update().get(id=instance.id)
                        skill_offering = instance.skill_offering_enrollment.skill_offering
                        partner_logo_url = None
                        if skill_offering.knowledge_partner_id:
                            if skill_offering.knowledge_partner.logo:
                                student = instance.skill_offering_enrollment.student

                                college_code = student.college.college_code if student.college_id else ''
                                year = timezone.now().strftime("%y")
                                branch_name = student.rbranch.name if student.rbranch_id else ''
                                college_name = student.college.college_name if student.college else ''
                                college_type = student.college.college_type
                                if college_type == 1:
                                    # ARTS_AND_SCIENCE
                                    certificate_no_pref = f'NM{year}AS'
                                elif college_type == 2:
                                    # ENGINEERING
                                    certificate_no_pref = f'NM{year}AU'
                                elif college_type == 4:
                                    # POLYTECHNIC
                                    certificate_no_pref = f'NM{year}P'
                                else:
                                    certificate_no_pref = f'NM{year}'

                                college_level_records = SKillOfferingEnrollmentCertificate.objects.select_for_update().filter(
                                    certificate_no__istartswith=certificate_no_pref,
                                    college_type=college_type,
                                    issue_at__isnull=False
                                ).order_by('-issue_at')
                                if college_level_records:
                                    last_record = college_level_records.first()
                                    if last_record.certificate_no:
                                        last_certificate_no = str(last_record.certificate_no).replace(
                                            certificate_no_pref, '')
                                        last_certificate_no = str(
                                            int(last_certificate_no)+1).zfill(8)
                                    else:
                                        last_certificate_no = '1'.zfill(8)
                                else:
                                    last_certificate_no = '1'.zfill(8)

                                # Fields
                                course_name = skill_offering.course_name  # "Python Programming"
                                training_partner_name = skill_offering.knowledge_partner.name if skill_offering.knowledge_partner_id else ''
                                # "NMG1003873"
                                certificate_no = f'{certificate_no_pref}{last_certificate_no}'.upper(
                                )
                                date = timezone.now().strftime("%d/%m/%Y")  # "12/12/2020"
                                name = student.aadhar_number  # "Sathish Kumar"
                                reg_no = student.roll_no  # "8276352AS726"

                                instance.data = {
                                    "FullName": student.aadhar_number,
                                    'StudentName': student.aadhar_number,
                                    'RollNo': reg_no,
                                    'Branch': branch_name,
                                    'CollegeName': college_name,
                                    'CourseName': course_name,
                                    'PartnerName': training_partner_name,
                                    'CertificateNo': certificate_no,
                                    'dateOfIssue': date,
                                }

                                # "https://naanmudhalvan.tn.gov.in/images/patners/aws.png"
                                partner_logo_url = skill_offering.knowledge_partner.logo.url

                                print("Flag 1")
                                # Open the image
                                image = Image.open(os.path.join(
                                    settings.BASE_DIR, 'skillofferings/certificate', 'certificate2.png'))

                                # Create an ImageDraw object
                                draw = ImageDraw.Draw(image)

                                # Choose a font and a font size
                                font = ImageFont.truetype(os.path.join(
                                    settings.BASE_DIR, 'skillofferings/certificate', 'Cardo/Cardo-Regular.ttf'), 60)
                                font_bold = ImageFont.truetype(os.path.join(
                                    settings.BASE_DIR, 'skillofferings/certificate', 'Cardo/Cardo-Bold.ttf'), 70)
                                font_bold_60 = ImageFont.truetype(os.path.join(
                                    settings.BASE_DIR, 'skillofferings/certificate', 'Cardo/Cardo-Bold.ttf'), 60)

                                print("Flag 2")
                                # Certificate Content
                                left_margin = 50
                                right_margin = 50
                                top_margin = 50
                                bottom_margin = 50

                                text = f"For the successful completion of {course_name} sponsored by Naan Mudhalvan Program,\nTamilnadu Skill Development Corporation and conducted by {training_partner_name}.\nDuring the course, the learner demonstrated initiative and commitment to advance in their career."
                                text_width, text_height = draw.textsize(
                                    text, font=font)

                                # # Calculate the position of the text
                                x = (image.width - text_width) / 2
                                y = (image.height - text_height) / 2
                                # # Draw the text on the image
                                draw.multiline_text((x, 1500), text, font=font, fill=(
                                    0, 0, 0), align="center", spacing=40)

                                draw.text((720, 1050), name,
                                          font=font_bold, fill=(0, 0, 0))
                                draw.text((2180, 1050), reg_no,
                                          font=font_bold, fill=(0, 0, 0))

                                draw.text((700, 1200), branch_name,
                                          font=font_bold, fill=(0, 0, 0))
                                draw.text((900, 1340), college_name,
                                          font=font_bold, fill=(0, 0, 0))

                                draw.text((120, 450), certificate_no,
                                          font=font_bold_60, fill=(0, 0, 0))

                                draw.text((480, image.height - 205), date,
                                          font=font_bold_60, fill=(0, 0, 0))

                                # draw Image from url partner_logo_url
                                # response = requests.get(partner_logo_url)
                                # partner_logo = Image.open(BytesIO(response.content))
                                #
                                partner_logo_url = f"{settings.BASE_DIR}{partner_logo_url}"
                                print("partner_logo_url", partner_logo_url)
                                print("BASE_DIR", settings.BASE_DIR)
                                print("partner_logo_url", )
                                # partner_logo = Image.open(partner_logo_url)
                                partner_logo = Image.open(
                                    partner_logo_url).convert("RGBA")

                                print("Flag 3")
                                # resize partner logo aspect ratio with 300px
                                maxsize = (300, 300)
                                partner_logo.thumbnail(
                                    maxsize, Image.Resampling.LANCZOS)

                                print("Flag 4")
                                image.paste(
                                    partner_logo, (image.width - 400, 150), partner_logo)

                                # QR Code
                                qr = qrcode.QRCode(box_size=5)
                                qr.add_data(
                                    f'portal.naanmudhalvan.tn.gov.in/validate/certificate/{instance.certificate_id}')
                                qr.make()
                                img_qr = qr.make_image()
                                image.paste(img_qr, (image.width - 350, 550))

                                print("Flag 4.1")
                                # Save the image
                                rgb_image = image.convert('RGB')

                                print("Flag 4.1")
                                rgb_image.thumbnail(
                                    (2000, 2000), Image.Resampling.LANCZOS)

                                print("Flag 4.1")
                                # file_path = f'media/skill_offering/certificates/{certificate_no}.png'
                                # rgb_image.save(os.path.join(settings.BASE_DIR, file_path), "JPEG", optimize=True, quality=80)
                                file_path = f'media/skill_offering/certificates/{certificate_no}.pdf'
                                rgb_image.save(os.path.join(
                                    settings.BASE_DIR, file_path), "pdf", optimize=True, quality=80)
                                print("Flag 5")
                                instance.certificate = f'skill_offering/certificates/{certificate_no}.pdf'
                                instance.certificate_no = certificate_no
                                instance.issue_at = timezone.now()
                                instance.college_type = college_type
                                print(f'certificate {instance.certificate}')
                                print(
                                    f'certificate_no {instance.certificate_no}')
                                instance.save()
                                sync_file_with_scp_with_path(file_path)
                                return None

                    except Exception as e:
                        # instance.data = {"error": str(e)}
                        # instance.save()
                        print("CERTIFICATE generation - ", e)

                        return None
        else:
            # instance.data = {"error": 'No skill_offering_id/ No student_id'}
            # instance.save()

            return None
    else:

        instance.data = {"error": 'No skill_offering_enrollment_id'}

        return None
        # instance.save()
    print("generate_certificate")
    return None


class SKillOfferingEnrollmentProgress(models.Model):
    skill_offering_enrollment = models.ForeignKey(SKillOfferingEnrollment, on_delete=models.SET_NULL, null=True,
                                                  blank=True)
    knowledge_partner = models.ForeignKey(
        KnowledgePartner, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ea_1 = models.CharField(null=True, blank=True, max_length=255)
    ea_2 = models.CharField(null=True, blank=True, max_length=255)
    ea_3 = models.CharField(null=True, blank=True, max_length=255)
    ia_1 = models.CharField(null=True, blank=True, max_length=100)
    ia_2 = models.CharField(null=True, blank=True, max_length=100)
    ia_3 = models.CharField(null=True, blank=True, max_length=100)
    ia_4 = models.CharField(null=True, blank=True, max_length=100)
    ia_5 = models.CharField(null=True, blank=True, max_length=100)
    internal_marks = models.CharField(null=True, blank=True, max_length=100)
    external_marks = models.CharField(null=True, blank=True, max_length=100)
    progress_percentage = models.FloatField(default=0)
    assessment_status = models.BooleanField(default=False)
    assessment_data = models.JSONField(blank=True, null=True)
    course_complete = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

# method for updating
# @receiver(post_save, sender=SKillOfferingEnrollmentProgress)
# def check_or_create_certificate(sender, instance, created, **kwargs):
#     if instance.progress_percentage > 50:
#         try:
#             enrollment_certificate = SKillOfferingEnrollmentCertificate.objects.get(
#                 skill_offering_enrollment_id=instance.skill_offering_enrollment_id
#             )
#
#         except SKillOfferingEnrollmentCertificate.DoesNotExist:
#             enrollment_certificate = SKillOfferingEnrollmentCertificate.objects.create(
#                 skill_offering_enrollment_id=instance.skill_offering_enrollment_id,
#                 knowledge_partner_id=instance.knowledge_partner_id,
#             )
#         generate_certificate(enrollment_certificate)


class MandatoryCourse(models.Model):
    college = models.ForeignKey(
        'college.college', blank=True, null=True, on_delete=models.SET_NULL)
    skill_offering = models.ForeignKey(
        SKillOffering, on_delete=models.SET_NULL, null=True, blank=True)
    course_type = models.IntegerField(default=0)  # 0 - free, 1 - paid
    is_unlimited = models.BooleanField(default=False)
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True)
    sem = models.IntegerField(null=True, blank=True)
    count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class TempA(models.Model):
    student = models.ForeignKey(
        'student.Student', on_delete=models.SET_NULL, null=True, blank=True)
    skill_offering_enrollment = models.ForeignKey(SKillOfferingEnrollment, on_delete=models.SET_NULL, null=True,
                                                  blank=True)
    access_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class CourseBulkUpload(models.Model):
    skill_offering = models.ForeignKey(
        SKillOffering, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to='coursera')
    # 0 - new, 1 - in progress, 2 - success, 3 - failed
    status = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    result_data = models.JSONField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    serial = models.CharField(max_length=255, null=True, blank=True)
    # 0 - coursera, 1 - Microsoft, 2 - Infosys
    course_type = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return str(self.id)


class FeedBack(models.Model):
    student = models.ForeignKey(
        'student.Student', null=True, blank=True, on_delete=models.SET_NULL)
    # Please select the course you were enrolled?
    enrollment = models.ForeignKey(
        SKillOfferingEnrollment, null=True, blank=True, on_delete=models.SET_NULL)
    skill_offering = models.ForeignKey(
        SKillOffering, null=True, blank=True, on_delete=models.SET_NULL)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    course_code = models.CharField(max_length=255, null=True, blank=True)
    # 2. Quality of the course
    quality_of_course = models.CharField(max_length=255, null=True, blank=True)
    # 3. Quality of Trainer
    quality_of_trainer = models.CharField(
        max_length=255, null=True, blank=True)
    # 4. Has the course increased your motivation to upskill?
    has_the_course_increased_your_motivation_to_upskill = models.CharField(
        max_length=255, null=True, blank=True)
    # 5. Did you have supportive teachers who could help with queries?
    did_you_have_supportive_teachers_who_could_help_with_queries = models.CharField(
        max_length=255, null=True, blank=True)
    # 6. Was the time allocated to you for the training and homework sufficient?
    time_allocated_to_you_for_the_training_and_homework_sufficient = models.CharField(
        max_length=255, null=True, blank=True)
    # 7. Were doubt-clearing sessions held by the trainer?
    doubt_clearing_sessions_held_by_the_trainer = models.CharField(
        max_length=255, null=True, blank=True)
    # 8. Did your doubts get cleared?
    doubts_get_cleared = models.CharField(
        max_length=255, null=True, blank=True)
    # 9. In your opinion, is hybrid training more effective than online training?
    is_hybrid_training_more_effective = models.CharField(
        max_length=255, null=True, blank=True)
    # 10. Do you think the  training was sufficient or would more days would be helpful?
    training_sufficient_with_days = models.CharField(
        max_length=255, null=True, blank=True)
    # 11. Would you be interested in learning and working on a larger project?
    interested_in_working_in_large_projects = models.CharField(
        max_length=255, null=True, blank=True)
    # 12. Do you want to repeat the training in the same topic  or learn advanced to suit the job market?
    repeat_the_training = models.CharField(
        max_length=255, null=True, blank=True)
    # 13. Mention the thing you enjoyed the most in this course
    enjoyment_in_course = models.TextField(null=True, blank=True)
    # 14. Any other course you would like to take?
    course_like_to_take = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)
