from celery import shared_task
from college.models import College
from ..models import Student, StudentRegistrationStepOne
import csv
from io import StringIO
import uuid
import re
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import Context
from django.conf import settings
from django.template.loader import get_template
from datarepo.models import StudentRegistrationStatus
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from nm_portal.config import Config

def check_email(email: str):
    regrex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regrex, email)


def get_uuid():
    uid = uuid.uuid4()
    return str(uid)[::-1].replace("-", '')


def send_email(_to, uid, college: bool = True, student: bool = False):
    """
    Send email to customer with order details.
    """
    try:
        if college:
            registration_url = Config.FRONT_END_URL + '/college-registration/%s' % uid
        elif student:
            registration_url = Config.FRONT_END_URL + '/student-registration/%s' % uid
        else:
            registration_url = 'https://google.com'
        message = get_template("emails/college_invite.html").render({'registration_url': registration_url})
        FROM_EAMIL = settings.EMAIL_HOST_FROM
        mail = EmailMessage(
            subject="Order confirmation",
            body=str(registration_url),
            from_email=FROM_EAMIL,
            to=[_to],
            reply_to=[FROM_EAMIL],
        )
        mail.fail_silently = False
        # mail.content_subtype = "html"
        send = mail.send()

        content = {
            'mail': str(send),
            'mail_dir': dir(send),
        }
        # from django.core.mail import EmailMultiAlternatives
        #
        # subject, from_email, to = 'NM Registration', 'chandumanikumar4@gmail.com', 'chandumanikumar5@gmail.com'
        # text_content = ''
        # html_content = str(message)
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()
    except Exception as e:
        print(e)
        return 0


@shared_task()
def async_task_student_invites(registration_step_one_id):
    step_one = StudentRegistrationStepOne.objects.select_related('college').get(id=registration_step_one_id)
    csv_file = step_one.csv_file.read().decode('utf-8')
    csv_data = csv.reader(StringIO(csv_file), delimiter=',')
    try:
        step_one.status = 1  # in-progress
        step_one.save()
        total_count = 0
        valid_count = 0
        invalid_count = 0
        already_exist_count = 0
        in_memory_student_list = []
        index = 0
        for row in csv_data:
            """
            File format
            first name,last name,roll no,email,mobile
            """
            index += 1
            if index != 1:
                # print(row)
                # print(get_uuid())
                total_count += 1
                if len(row) >= 5:

                    first_name = row[0]
                    last_name = row[1]
                    roll_no = row[2]
                    email = row[3]
                    mobile = row[4]

                    if email and mobile and roll_no:

                        check_student = Student.objects.values('id').filter(phone_number=mobile, email=email, college_id=step_one.college_id).exists()
                        check_student_email = Student.objects.values('id').filter(email=email).exists()

                        if check_student or check_student_email:
                            already_exist_count += 1
                        else:
                            new_student = Student(
                                invitation_id=get_uuid(),
                                step_one_id=registration_step_one_id,
                                college_id=step_one.college_id,
                                email=email,
                                phone_number=mobile,
                                first_name=first_name,
                                last_name=last_name,
                                roll_no=str(roll_no).strip().replace(" ", ""),
                                registration_status=StudentRegistrationStatus.INVITE_SEND,
                                degree=step_one.college.college_type if step_one.college_id else None,
                                affiliated_university_id=step_one.college.affiliated_university_id if step_one.college_id else None,

                            )
                            valid_count += 1
                            in_memory_student_list.append(new_student)
                    else:
                        invalid_count += 1
                else:
                    invalid_count += 1
        all_records_mailed = True
        if in_memory_student_list:
            bulk_insert_students = Student.objects.bulk_create(in_memory_student_list)
            for record in bulk_insert_students:
                try:
                    try:
                        # registration_url = 'http://0.0.0.0:2022/registration/' + str(record.invitation_id)
                        registration_url = settings.FRONT_END_URL + '/student-registration/' + str(record.invitation_id)
                        message = get_template("emails/student_invite.html").render({
                            'registration_url': registration_url
                        })
                        from_email = settings.EMAIL_HOST_FROM
                        mail = EmailMultiAlternatives(
                            "Invitation to Naan Mudhalvan",
                            message,
                            from_email=from_email,
                            to=[record.email],
                        )
                        mail.content_subtype = "html"
                        mail.mixed_subtype = 'related'
                        mail.attach_alternative(message, "text/html")
                        send = mail.send()
                        record.is_mailed = True
                    except Exception as e:
                        print(str(e))
                        all_records_mailed = False
                except Exception as e:
                    # print(get_uuid())
                    print("Error at Mail", str(e))
                    all_records_mailed = False

        step_one.total_count = total_count
        step_one.valid_count = valid_count
        step_one.invalid_count = invalid_count
        step_one.already_exist_count = already_exist_count
        step_one.status = 2  # completed
        step_one.is_mailed = all_records_mailed
        step_one.save()
        return {"message": "Done"}
    except Exception as e:
        step_one.status = 3  # failed
        step_one.save()
        return {"error": str(e)}
