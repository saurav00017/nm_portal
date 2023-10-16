from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from ..models import Student, StudentPaymentDetail, StudentConcessions, StudentRegistrationStepOne
from datarepo.models import AccountRole, District, StudentRegistrationStatus, StudentCaste
from users.models import User, UserDetail
from datarepo.models import PaymentStatus
from django.template import Context
from django.db.models import F
from django.template.loader import get_template
from cerberus import Validator
import yaml
import jwt
from django.utils.timezone import datetime, timedelta
import os
from users.views import MyTokenObtainPairSerializer
from nm_portal.config import Config
from .task import async_task_student_invites
import json
import razorpay
from college.models import College

RAZORPAY_USERNAME = os.environ.get('RAZORPAY_KEY', '')
RAZORPAY_SECRET_KEY = os.environ.get('RAZORPAY_SECRET_KEY', '')

RAZORPAY_USERNAME = "rzp_test_TPNYwIheW2VPhC"
RAZORPAY_SECRET_KEY = "Y5mbKfcfdlwludb231FdHhiO"

nm_razorpay_client = razorpay.Client(auth=(RAZORPAY_USERNAME, RAZORPAY_SECRET_KEY))
nm_razorpay_client.set_app_details({"title": "django", "version": "3"})


# Create your views here.


# TODO validate can invite the student to his college
@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def invite_student(request):
    """
    :param request: student details
    :return: 200 if success else 400 with error message
    1. parse all student details
    2. validate them
    3. record in db and send an email
    """
    account_role = \
        jwt.decode(request.headers['Authorization'][7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])[
            'account_role']
    is_compact = request.POST.get('is_compact', False)
    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        user_details = UserDetail.objects.get(user_id=request.user.id)
        is_compact = True if is_compact == 'true' else False
        if is_compact:
            roll_number = request.POST.get('roll_number', None)
            is_temporary_roll_number = request.POST.get('is_temporary_roll_number', None)
            name = request.POST.get('aadhar_number', None)
            sem = request.POST.get('sem', None)
            email = request.POST.get('email', None)
            year_of_study = request.POST.get('year_of_study', None)
            phone_number = request.POST.get('phone_number', None)
            branch_id = request.POST.get('branch_id', None)
            if roll_number is None or name is None or (
                    sem is None and year_of_study is None) or email is None or phone_number is None or branch_id is None:
                return Response(
                    {'message': 'roll_number, name, branch,sem/year_of_study, email, phone_number are required'},
                    status=status.HTTP_400_BAD_REQUEST)

            if is_temporary_roll_number:
                try:
                    is_temporary_roll_number = int(is_temporary_roll_number)
                except:
                    return Response(
                        {'message': 'Please provide valid is_temporary_roll_number'},
                        status=status.HTTP_400_BAD_REQUEST)

            if user_details.college_id:
                if user_details.college.college_type == 1:
                    roll_number = str(user_details.college.college_code).strip() + str(roll_number).strip()
            check_student_roll = Student.objects.filter(roll_no__iexact=roll_number,
                                                        college_id=user_details.id).exists()
            if check_student_roll:
                return Response(
                    {'message': 'Student roll_number already exists'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_details = UserDetail.objects.get(user_id=request.user.id)
                new_student = Student.objects.create(
                    roll_no=roll_number,
                    aadhar_number=name,
                    phone_number=int(phone_number) if phone_number else None,
                    email=email,
                    rbranch_id=branch_id,
                    sem=sem,
                    year_of_study=year_of_study,
                    college_id=user_details.college_id,
                    # degree=int(degree) if degree else None,
                    degree=user_details.college.college_type if user_details.college_id else None,
                    affiliated_university_id=user_details.college.affiliated_university_id if user_details.college else None,
                    # district_id=int(district_id) if district_id else None,
                    # current_address=current_address,
                    # permanent_address=permanent_address,
                    verification_status=1,
                    registration_status=4,
                    is_temporary_roll_number=False if is_temporary_roll_number is None else is_temporary_roll_number
                )
                new_student.save()
                #
                return Response(
                    {'message': 'student has been added',
                     'data': {
                         'student_id': new_student.id,
                     }},
                    status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'message': str(e)},
                    status=status.HTTP_400_BAD_REQUEST)
        try:
            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            roll_no = request.POST.get('roll_no', None)
            is_temporary_roll_number = request.POST.get('is_temporary_roll_number', None)
            year_of_study = request.POST.get('year_of_study', None)
            caste = request.POST.get('caste', None)
            certificate = request.FILES.get('certificate', None)
            aadhar_number = request.POST.get('aadhar_number', None)

            phone_number = request.POST.get('phone_number', None)
            email = request.POST.get('email', None)
            dob = request.POST.get('dob', None)
            gender = request.POST.get('gender', None)
            degree = request.POST.get('degree', None)
            specialization = request.POST.get('specialization', None)
            affiliated_university_id = request.POST.get('affiliated_university_id', None)
            # district_id = request.POST.get('district_id', None)
            # current_address = request.POST.get('current_address', None)
            # permanent_address = request.POST.get('permanent_address', None)
            hall_ticket_number = request.POST.get('hall_ticket_number', None)
            year_of_graduation = request.POST.get('year_of_graduation', None)
            tenth_pass_out_year = request.POST.get('tenth_pass_out_year', None)
            tenth_cgpa = request.POST.get('tenth_cgpa', None)
            intermediate_pass_out_year = request.POST.get('intermediate_pass_out_year', None)
            is_first_year_in_degree = True if request.POST.get('is_first_year_in_degree', None) == 'true' else False
            current_graduation_cgpa = request.POST.get('current_graduation_cgpa', None)
            has_backlogs = True if request.POST.get('has_backlogs', None) == 'true' else False

            if is_temporary_roll_number:
                try:
                    is_temporary_roll_number = int(is_temporary_roll_number)
                except:
                    return Response(
                        {'message': 'Please provide valid is_temporary_roll_number'},
                        status=status.HTTP_400_BAD_REQUEST)
            try:
                caste = int(caste)
            except:
                caste = None

            if email is None or first_name is None or last_name is None or roll_no is None or year_of_study is None or phone_number is None:
                return Response(
                    {'message': 'first_name, last_name, roll_no,year_of_study, phone_number, email are required'},
                    status=status.HTTP_400_BAD_REQUEST)

            concessions = None
            if caste in [StudentCaste.SC, StudentCaste.ST]:
                concessions = StudentConcessions.NEW
                if certificate is None:
                    return Response({'message': 'Please upload the certificate'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif certificate._size > Config.FILE_UPLOAD_MAX_MEMORY_SIZE:
                    return Response({'message': 'Please upload the certificate with max size 2Mb'},
                                    status=status.HTTP_400_BAD_REQUEST)

            user_details = UserDetail.objects.get(user_id=request.user.id)
            if user_details.college_id:
                if user_details.college.college_type == 1:
                    roll_no = str(user_details.college.college_code).strip() + str(roll_no).strip()

            try:
                check_student = Student.objects.values('id').get(phone_number=phone_number, email=email,
                                                                 college_id=user_details.college_id)
                check_student_email = Student.objects.values('id').get(email=email)
                return Response({'message': 'student/ email already invited'}, status=status.HTTP_400_BAD_REQUEST)
            except Student.DoesNotExist:
                check_student_roll_no = Student.objects.filter(roll_no__iexact=roll_no,
                                                               college_id=user_details.college_id).exists()
                if check_student_roll_no:
                    return Response({'message': 'Student roll number already exists'},
                                    status=status.HTTP_400_BAD_REQUEST)

                new_student = Student.objects.create(first_name=first_name,
                                                     last_name=last_name,
                                                     roll_no=roll_no,
                                                     is_temporary_roll_number=False if is_temporary_roll_number is None else is_temporary_roll_number,
                                                     certificate=certificate,
                                                     caste=int(caste) if caste else None,
                                                     concessions=concessions,
                                                     aadhar_number=aadhar_number,
                                                     phone_number=int(phone_number) if phone_number else None,
                                                     email=email,
                                                     dob=dob,
                                                     gender=int(gender) if gender else None,
                                                     college_id=user_details.college_id,
                                                     # degree=int(degree) if degree else None,
                                                     degree=user_details.college.college_type if user_details.college_id else None,
                                                     specialization=specialization,
                                                     affiliated_university_id=user_details.college.affiliated_university_id if user_details.college else None,
                                                     # district_id=int(district_id) if district_id else None,
                                                     # current_address=current_address,
                                                     # permanent_address=permanent_address,
                                                     hall_ticket_number=hall_ticket_number,
                                                     year_of_graduation=int(
                                                         year_of_graduation) if year_of_graduation else None,
                                                     year_of_study=int(year_of_study) if year_of_study else None,
                                                     tenth_pass_out_year=tenth_pass_out_year,
                                                     tenth_cgpa=tenth_cgpa,
                                                     intermediate_pass_out_year=intermediate_pass_out_year,
                                                     is_first_year_in_degree=is_first_year_in_degree,
                                                     current_graduation_cgpa=current_graduation_cgpa,
                                                     has_backlogs=has_backlogs,
                                                     added_by_id=request.user.id)
                new_student.save()
                print(new_student)
                registration_url = Config.FRONT_END_URL + '/student-registration/' + str(new_student.invitation_id)
                message = get_template("emails/student_invite.html").render({
                    'registration_url': registration_url
                })
                from_email = settings.EMAIL_HOST_FROM
                mail = EmailMultiAlternatives(
                    "Invitation to Naan Mudhalvan",
                    message,
                    from_email=from_email,
                    to=[email],
                )
                mail.content_subtype = "html"
                mail.mixed_subtype = 'related'
                mail.attach_alternative(message, "text/html")
                send = mail.send()
                new_student.registration_status = StudentRegistrationStatus.INVITE_SEND
                new_student.is_mailed = True
                new_student.save()
                return Response({'message': 'Student invited successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': "Student already exist", "error": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error 1 ", e)
            return Response({'message': 'Please contact admin'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'message': 'Only college admin can invite student'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def student_bulk_invites(request):
    """
    :param request: csv_file

    if -> account_role -> NM admin or NM staff
        1. create RegistrationStepOne Model
        2. start the celery task
            a. loop all the records and create TempRegistration record
    else  -> access Permission error

    :return:
    """
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']

    csv_file = request.FILES.get('csv_file', None)
    print(account_role, account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF])

    if account_role in [AccountRole.COLLEGE_ADMIN, AccountRole.COLLEGE_ADMIN_STAFF]:
        if csv_file:
            try:
                # College ADMIN or College admin staff
                user_validation = User.objects.filter(id=request.user.id, account_role=account_role,
                                                      is_active=1).exists()
                if user_validation:
                    user_profile = UserDetail.objects.get(user_id=request.user.id)

                    new_step_one = StudentRegistrationStepOne.objects.create(
                        csv_file=csv_file,
                        user_id=request.user.id,
                        college_id=user_profile.college_id
                    )
                    print(new_step_one)
                    initiate_background_task = async_task_student_invites.delay(
                        registration_step_one_id=new_step_one.id)

                    print(initiate_background_task)
                    content = {
                        "message": "task initiated"
                    }
                    return Response(content, status.HTTP_200_OK, content_type='application/json')
                else:
                    content = {
                        "message": "You don't have the permissions"
                    }
                    return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
            except UserDetail.DoesNotExist:
                content = {
                    "message": "Please contact admin"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        else:
            content = {
                "message": "Please provide file"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "You dont have a permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')


@api_view(['GET', 'POST'])
def student_registration(request, invitation_id: str):
    regrex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    """
    :Public_endpoint
    :param request: invitation_id

    if invitation_id is valid from College Model with status=0
        if :GET - get_details
            :return College basic details
        elif :POST - update_details
            1. update the details
            2. generate razor pay ID
            :return razor details

    else
        :return Invalid invitation_id
    """

    if invitation_id:
        if request.method == 'GET':
            try:
                get_student = Student.objects.annotate(
                    affiliated_university_name=F('affiliated_university__name'),
                ).values(
                    'id',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'email',
                    'degree',
                    'affiliated_university_id',
                    'affiliated_university_name',
                    'year_of_study',
                    'roll_no',
                    'registration_status',
                ).get(invitation_id=invitation_id, registration_status__in=[
                    StudentRegistrationStatus.INVITE_SEND,
                    StudentRegistrationStatus.REGISTRATION_IN_PROGRESS,
                    StudentRegistrationStatus.REGISTRATION_COMPLETE], subscription_status=False)
                student_id = get_student['id']
                student_status = get_student['registration_status']
                del get_student['id']
                del get_student['registration_status']
                content = {
                    'payment_details': None,
                    'student_details': dict(get_student)
                }
                if student_status == StudentRegistrationStatus.REGISTRATION_COMPLETE:
                    get_subscription = StudentPaymentDetail.objects.values('razorpay_order_id',
                                                                           'registration_fee').filter(
                        student_id=student_id, payment_status=PaymentStatus.INITIATE).order_by('-id').first()
                    if get_subscription:
                        content['payment_details'] = {
                            "payment_status": PaymentStatus.INITIATE,
                            "order_id": get_subscription['razorpay_order_id'],
                            "amount": get_subscription['registration_fee'] / 100,
                        }

                return Response(content, status.HTTP_200_OK, content_type='application/json')
            except Student.DoesNotExist:
                content = {
                    "message": "invalid invitation ID"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        elif request.method == 'POST':
            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            roll_no = request.POST.get('roll_no', None)
            is_temporary_roll_number = request.POST.get('is_temporary_roll_number', None)
            phone_number = request.POST.get('phone_number', None)

            is_pass_out = request.POST.get('is_pass_out', None)
            provisional_certificate = request.FILES.get('provisional_certificate', None)

            caste = request.POST.get('caste', None)
            certificate = request.FILES.get('certificate', None)

            aadhar_number = request.POST.get('aadhar_number', None)
            email = request.POST.get('email', None)
            dob = request.POST.get('dob', None)
            gender = request.POST.get('gender', None)
            # degree = request.POST.get('degree', None)
            specialization = request.POST.get('specialization', None)
            # district_id = request.POST.get('district_id', None)
            hall_ticket_number = request.POST.get('hall_ticket_number', None)
            year_of_study = request.POST.get('year_of_study', None)
            year_of_graduation = request.POST.get('year_of_graduation', None)

            # current_address = request.POST.get('current_address', None)
            current_address = request.POST.get('current_address', None)
            current_village = request.POST.get('current_village', None)
            current_town_city = request.POST.get('current_town_city', None)
            current_district = request.POST.get('current_district', None)
            current_state = request.POST.get('current_state', None)
            current_pincode = request.POST.get('current_pincode', None)

            permanent_address = request.POST.get('permanent_address', None)
            permanent_address = request.POST.get('permanent_address', None)
            # permanent_landmark = request.POST.get('permanent_landmark', None)
            # permanent_mandal = request.POST.get('permanent_mandal', None)
            permanent_village = request.POST.get('permanent_village', None)
            permanent_town_city = request.POST.get('permanent_town_city', None)
            permanent_district = request.POST.get('permanent_district', None)
            permanent_state = request.POST.get('permanent_state', None)
            permanent_pincode = request.POST.get('permanent_pincode', None)

            # user_credentials
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)

            request_schema = '''
                first_name:
                    type: string
                    empty: false
                    required: true
                last_name:
                    type: string
                    empty: false
                    required: true
                phone_number:
                    type: string
                    empty: false
                    required: true
                    min: 10
                    max: 10
                roll_no:
                    type: string
                    empty: false
                    required: true
                gender:
                    type: string
                    empty: false
                    required: true
                caste:
                    type: string
                    empty: false
                    required: true
                certificate:
                    type: string
                    empty: true
                    required: false
                is_pass_out:
                    type: string
                    empty: true
                    required: false
                provisional_certificate:
                    type: string
                    empty: true
                    required: false
                aadhar_number:
                    type: string
                    empty: true
                    required: false
                email:
                    type: string
                    empty: false
                    required: true
                dob:
                    type: string
                    empty: false
                    required: true
                specialization:
                    type: string
                    empty: false
                    required: true
                specialization:
                    type: string
                    empty: false
                    required: true
                hall_ticket_number:
                    type: string
                    empty: true
                    required: false
                year_of_study:
                    type: string
                    empty: false
                    required: true
                    min: 4
                    max: 4
                year_of_graduation:
                    type: string
                    empty: true
                    required: false
                    min: 4
                    max: 4
                username:
                    type: string
                    empty: false
                    required: true
                    
                password:
                    type: string
                    empty: false
                    required: true
                    
                    
                current_address:
                    type: string
                    empty: true
                    required: false
                    
                
                current_village:
                    type: string
                    empty: true
                    required: false
                    
                current_town_city:
                    type: string
                    empty: true
                    required: false
                    
                current_district:
                    type: string
                    empty: true
                    required: false
                    
                current_state:
                    type: string
                    empty: true
                    required: false
                    
                current_pincode:
                    type: string
                    empty: true
                    required: false
                    
                permanent_address:
                    type: string
                    empty: true
                    required: false
                    
                permanent_village:
                    type: string
                    empty: true
                    required: false
                    
                    
                permanent_town_city:
                    type: string
                    empty: true
                    required: false
                    
                permanent_district:
                    type: string
                    empty: true
                    required: false
                permanent_pincode:
                    type: string
                    empty: true
                    required: false
                permanent_state:
                    type: string
                    empty: true
                    required: false
                '''
            v = Validator()
            post_data = request.POST.dict()
            schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
            if v.validate(post_data, schema):
                try:
                    if username and len(str(password)) >= 8:
                        try:
                            get_student = Student.objects.get(invitation_id=invitation_id, registration_status__in=[
                                StudentRegistrationStatus.INVITE_SEND,
                                StudentRegistrationStatus.REGISTRATION_IN_PROGRESS])
                            # try:
                            #     get_current_district = District.objects.get(id=int(current_district_id))
                            # except District.DoesNotExist:
                            #     content = {
                            #         "message": "Please provide valid current district ID"
                            #     }
                            #     return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                            # try:
                            #     get_permanent_district = District.objects.get(id=int(permanent_district_id))
                            # except District.DoesNotExist:
                            #     content = {
                            #         "message": "Please provide valid permanent district ID"
                            #     }
                            #     return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                            try:
                                get_student.first_name = first_name
                                get_student.last_name = last_name
                                # get_student.roll_no = roll_no
                                get_student.phone_number = phone_number
                                get_student.caste = caste
                                get_student.certificate = certificate if certificate else None
                                get_student.concessions = StudentConcessions.FILE_UPLOADED if certificate else get_student.concessions
                                get_student.aadhar_number = aadhar_number
                                get_student.email = email
                                get_student.dob = dob
                                get_student.gender = gender
                                get_student.specialization = specialization
                                # current
                                get_student.current_address = current_address
                                get_student.current_village = current_village
                                get_student.current_town_city = current_town_city
                                get_student.current_state = current_state
                                get_student.current_district = current_district
                                # get_student.current_plot_no_and_street = current_plot_no_and_street
                                get_student.current_pincode = int(current_pincode) if current_pincode else None
                                # Permanent
                                get_student.permanent_address = permanent_address
                                get_student.permanent_village = permanent_village
                                get_student.permanent_town_city = permanent_town_city
                                # get_student.permanent_village_panchayat_colony = permanent_village_panchayat_colony
                                # get_student.permanent_mandal_town_area = permanent_mandal_town_area
                                get_student.permanent_state = permanent_state
                                get_student.permanent_district = permanent_district
                                get_student.permanent_pincode = int(permanent_pincode) if permanent_pincode else None

                                get_student.hall_ticket_number = hall_ticket_number
                                get_student.year_of_study = year_of_study
                                get_student.year_of_graduation = year_of_graduation

                                if get_student.is_temporary_roll_number == 1:
                                    if is_temporary_roll_number:
                                        if is_temporary_roll_number == '0' or is_temporary_roll_number == 0:
                                            get_student.is_temporary_roll_number = 0
                                            get_student.roll_no = roll_no
                                        else:
                                            try:
                                                is_temporary_roll_number = int(is_temporary_roll_number)
                                            except:
                                                pass

                                # create college_admin
                                new_student_user = User.create_registered_user(
                                    username=username,
                                    password=password,
                                    mobile=phone_number,
                                    email=email,
                                    account_role=AccountRole.STUDENT,
                                    student_id=get_student.id,
                                )
                                get_student.registration_status = StudentRegistrationStatus.PAYMENT_COMPLETE
                                get_student.save()
                                try:
                                    # Razor Pay
                                    order_currency = 'INR'
                                    order_receipt = 'NM_S' + invitation_id
                                    razorpay_amount = Config(caste=get_student.caste,
                                                             college_type=get_student.degree).STUDENT_SUBSCRIPTION_FEE
                                    data = {
                                        'amount': int(razorpay_amount),
                                        'currency': order_currency,
                                        'receipt': order_receipt,
                                    }
                                    # print(data)
                                    order_details = nm_razorpay_client.order.create(data=data)
                                    razorpay_order_id = order_details['id']
                                    new_student_subscription = StudentPaymentDetail.objects.create(
                                        student_id=get_student.id,
                                        registration_fee=razorpay_amount,
                                        razorpay_order_id=razorpay_order_id,
                                        razorpay_order_receipt=order_receipt,
                                        razorpay_created_at=order_details[
                                            'created_at'] if 'created_at' in order_details else None,
                                        payment_mode=0,  # Online
                                        payment_status=PaymentStatus.INITIATE,  # initiate
                                    )

                                    student_refresh_token = MyTokenObtainPairSerializer.get_token(new_student_user)
                                    content = {
                                        "first_name": get_student.first_name,
                                        "last_name": get_student.last_name,
                                        'payment_status': 0,  # Need to pay
                                        'order_id': razorpay_order_id,
                                        'amount': razorpay_amount,
                                        "username": new_student_user.username,
                                        "name": new_student_user.name,
                                        'refresh': str(student_refresh_token),
                                        'access': str(student_refresh_token.access_token)
                                    }
                                    return Response(content, status.HTTP_200_OK, content_type='application/json')

                                except Exception as e:
                                    content = {
                                        "message": "Registration done successfully. Payment",
                                        'error': str(e)
                                    }
                                    return Response(content, status.HTTP_400_BAD_REQUEST,
                                                    content_type='application/json')

                            except Exception as e:
                                content = {
                                    "message": "Please provide valid data",
                                    'error': str(e)
                                }
                                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                        except Student.DoesNotExist:

                            content = {
                                "message": "invalid invitation ID/ already registered"
                            }
                            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        content = {
                            "message": "Please provide valid college admin credentials"
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Exception as e:
                    content = {
                        "message": "Please provide valid credentials",
                        'error': str(e)
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    'message': "invalid request",
                    'errors': v.errors
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    else:
        content = {
            "message": "Please provide invitation ID"
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
def pass_out_student_registration(request):
    """
    :Public_endpoint
    :param request: invitation_id

    if :POST - update_details
        1. update the details
        2. generate razor pay ID
        :return razor details

    else
        :return Invalid request
    """

    first_name = request.POST.get('first_name', None)
    last_name = request.POST.get('last_name', None)
    roll_no = request.POST.get('roll_no', None)
    is_temporary_roll_number = request.POST.get('is_temporary_roll_number', None)
    phone_number = request.POST.get('phone_number', None)

    is_pass_out = request.POST.get('is_pass_out', None)
    provisional_certificate = request.FILES.get('provisional_certificate', None)

    caste = request.POST.get('caste', None)
    college_id = request.POST.get('college_id', None)
    certificate = request.FILES.get('certificate', None)

    aadhar_number = request.POST.get('aadhar_number', None)
    aadhar_number = request.POST.get('full_name', None)
    email = request.POST.get('email', None)
    dob = request.POST.get('dob', None)
    gender = request.POST.get('gender', None)
    # degree = request.POST.get('degree', None)
    specialization = request.POST.get('specialization', None)
    # district_id = request.POST.get('district_id', None)
    hall_ticket_number = request.POST.get('hall_ticket_number', None)
    year_of_study = request.POST.get('year_of_study', None)
    year_of_graduation = request.POST.get('year_of_graduation', None)

    # current_address = request.POST.get('current_address', None)
    current_address = request.POST.get('current_address', None)
    current_village = request.POST.get('current_village', None)
    current_town_city = request.POST.get('current_town_city', None)
    current_district = request.POST.get('current_district', None)
    current_state = request.POST.get('current_state', None)
    current_pincode = request.POST.get('current_pincode', None)

    permanent_address = request.POST.get('permanent_address', None)
    permanent_address = request.POST.get('permanent_address', None)
    # permanent_landmark = request.POST.get('permanent_landmark', None)
    # permanent_mandal = request.POST.get('permanent_mandal', None)
    permanent_village = request.POST.get('permanent_village', None)
    permanent_town_city = request.POST.get('permanent_town_city', None)
    permanent_district = request.POST.get('permanent_district', None)
    permanent_state = request.POST.get('permanent_state', None)
    permanent_pincode = request.POST.get('permanent_pincode', None)

    tenth_pass_out_year = request.POST.get('tenth_pass_out_year', None)
    tenth_cgpa = request.POST.get('tenth_cgpa', None)
    intermediate_pass_out_year = request.POST.get('intermediate_pass_out_year', None)
    is_first_year_in_degree = True if request.POST.get('is_first_year_in_degree', None) == 'true' else False
    current_graduation_cgpa = request.POST.get('current_graduation_cgpa', None)
    has_backlogs = True if request.POST.get('has_backlogs', None) == 'true' else False

    # user_credentials
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    request_schema = '''
        college_id:
            type: string
            empty: true
            required: false
        full_name:
            type: string
            empty: true
            required: false
        tenth_pass_out_year:
            type: string
            empty: true
            required: false
        tenth_cgpa:
            type: string
            empty: true
            required: false
        intermediate_pass_out_year:
            type: string
            empty: true
            required: false
        is_first_year_in_degree:
            type: string
            empty: true
            required: false
        current_graduation_cgpa:
            type: string
            empty: true
            required: false
        has_backlogs:
            type: string
            empty: true
            required: false
        first_name:
            type: string
            empty: true
            required: false
        last_name:
            type: string
            empty: true
            required: false
        phone_number:
            type: string
            empty: true
            required: false
            min: 10
            max: 10
        roll_no:
            type: string
            empty: true
            required: false
        gender:
            type: string
            empty: true
            required: false
        caste:
            type: string
            empty: true
            required: false
        certificate:
            type: string
            empty: true
            required: false
        provisional_certificate:
            type: string
            empty: true
            required: false
        aadhar_number:
            type: string
            empty: true
            required: false
        email:
            type: string
            empty: false
            required: true
        dob:
            type: string
            empty: true
            required: false
        specialization:
            type: string
            empty: true
            required: false
        specialization:
            type: string
            empty: true
            required: false
        hall_ticket_number:
            type: string
            empty: true
            required: false
        year_of_study:
            type: string
            empty: true
            required: false
            min: 4
            max: 4
        year_of_graduation:
            type: string
            empty: true
            required: false
            min: 4
            max: 4
        username:
            type: string
            empty: false
            required: true
            
        password:
            type: string
            empty: false
            required: true
            
            
        current_address:
            type: string
            empty: true
            required: false
            
        
        current_village:
            type: string
            empty: true
            required: false
            
        current_town_city:
            type: string
            empty: true
            required: false
            
        current_district:
            type: string
            empty: true
            required: false
            
        current_state:
            type: string
            empty: true
            required: false
            
        current_pincode:
            type: string
            empty: true
            required: false
            
        permanent_address:
            type: string
            empty: true
            required: false
            
        permanent_village:
            type: string
            empty: true
            required: false
            
            
        permanent_town_city:
            type: string
            empty: true
            required: false
            
        permanent_district:
            type: string
            empty: true
            required: false
        permanent_pincode:
            type: string
            empty: true
            required: false
        permanent_state:
            type: string
            empty: true
            required: false
        is_temporary_roll_number:
            type: string
            empty: true
            required: false
        '''
    v = Validator()
    post_data = request.POST.dict()
    schema = yaml.load(request_schema, Loader=yaml.SafeLoader)
    if v.validate(post_data, schema):
        try:
            if provisional_certificate is None:
                content = {
                    "message": "Please provide provisional certificate"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if caste:
                if int(caste) in [StudentCaste.SC, StudentCaste.ST]:
                    if certificate is None:
                        content = {
                            "message": "Please provide certificate"
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            if username:
                get_college = None
                try:
                    if is_temporary_roll_number:
                        try:
                            is_temporary_roll_number = int(is_temporary_roll_number)
                        except:
                            is_temporary_roll_number = False
                    else:
                        is_temporary_roll_number = False
                    if college_id:
                        get_college = College.objects.get(id=int(college_id))

                    check_student_email = Student.objects.filter(email__iexact=email).exists()
                    if check_student_email:
                        content = {
                            "message": "Student with email already exist",
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    check_student_roll_no = Student.objects.filter(roll_no__iexact=email).exists()
                    if check_student_roll_no:

                        content = {
                            "message": "Student with roll number already exist",
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        if get_college.college_type == 1:
                            roll_no = str(get_college.college_code).strip() + str(roll_no).strip()
                        else:
                            roll_no = str(roll_no).strip()
                        new_student = Student.objects.create(
                            is_pass_out=True,
                            provisional_certificate=provisional_certificate,
                            first_name=first_name,
                            last_name=last_name,
                            roll_no=roll_no,
                            is_temporary_roll_number=is_temporary_roll_number,
                            certificate=certificate,
                            caste=int(caste) if caste else None,
                            concessions=StudentConcessions.FILE_UPLOADED,
                            aadhar_number=aadhar_number,
                            phone_number=int(phone_number) if phone_number else None,
                            email=email,
                            dob=dob,
                            gender=int(gender) if gender else None,
                            college_id=get_college.id if get_college else None,
                            # degree=int(degree) if degree else None,
                            degree=get_college.college_type if get_college else None,
                            specialization=specialization,
                            affiliated_university_id=get_college.affiliated_university_id if get_college else None,
                            # district_id=int(district_id) if district_id else None,
                            # current_address=current_address,
                            # permanent_address=permanent_address,
                            hall_ticket_number=hall_ticket_number,
                            year_of_graduation=int(year_of_graduation) if year_of_graduation else None,
                            year_of_study=int(year_of_study) if year_of_study else None,
                            tenth_pass_out_year=tenth_pass_out_year,
                            tenth_cgpa=tenth_cgpa,
                            intermediate_pass_out_year=intermediate_pass_out_year,
                            is_first_year_in_degree=is_first_year_in_degree,
                            current_graduation_cgpa=current_graduation_cgpa,
                            has_backlogs=has_backlogs,
                            added_by_id=request.user.id,
                            registration_status=StudentRegistrationStatus.PENDING_APPROVAL)

                        # current
                        new_student.current_address = current_address
                        new_student.current_village = current_village
                        new_student.current_town_city = current_town_city
                        new_student.current_state = current_state
                        new_student.current_district = current_district
                        new_student.current_pincode = int(current_pincode) if current_pincode else None
                        # Permanent
                        new_student.permanent_address = permanent_address
                        new_student.permanent_village = permanent_village
                        new_student.permanent_town_city = permanent_town_city
                        new_student.permanent_state = permanent_state
                        new_student.permanent_district = permanent_district
                        new_student.permanent_pincode = int(permanent_pincode) if permanent_pincode else None
                        new_student.save()
                    try:
                        new_student_user = User.create_registered_user(
                            username=username,
                            password=password,
                            mobile=phone_number,
                            email=email,
                            account_role=AccountRole.STUDENT,
                            student_id=new_student.id,
                        )
                        new_student.registration_status = StudentRegistrationStatus.PENDING_APPROVAL
                        new_student.save()
                        try:
                            # Razor Pay
                            # order_currency = 'INR'
                            # order_receipt = 'NM_S' + new_student.invitation_id
                            # razorpay_amount = Config(caste=new_student.caste, college_type=new_student.degree).STUDENT_SUBSCRIPTION_FEE
                            # data = {
                            #     'amount': int(razorpay_amount),
                            #     'currency': order_currency,
                            #     'receipt': order_receipt,
                            # }
                            # # print(data)
                            # order_details = nm_razorpay_client.order.create(data=data)
                            # razorpay_order_id = order_details['id']
                            # new_student_subscription = StudentPaymentDetail.objects.create(
                            #     student_id=new_student.id,
                            #     registration_fee=razorpay_amount,
                            #     razorpay_order_id=razorpay_order_id,
                            #     razorpay_order_receipt=order_receipt,
                            #     razorpay_created_at=order_details['created_at'] if 'created_at' in order_details else None,
                            #     payment_mode=0,  # Online
                            #     payment_status=PaymentStatus.INITIATE,  # initiate
                            # )
                            #
                            student_refresh_token = MyTokenObtainPairSerializer.get_token(new_student_user)
                            content = {
                                "first_name": new_student.first_name,
                                "last_name": new_student.last_name,
                                "registration_status": new_student.registration_status,
                                'payment_status': 2,  # Need to pay
                                'order_id': "razorpay_order_id",
                                'amount': "razorpay_amount",
                                "username": new_student_user.username,
                                "name": new_student_user.name,
                                'refresh': str(student_refresh_token),
                                'access': str(student_refresh_token.access_token),
                                "message": "Please contact college admin for approval",
                            }
                            return Response(content, status.HTTP_200_OK, content_type='application/json')

                        except Exception as e:
                            content = {
                                "message": "Registration done successfully. Payment",
                                'error': str(e)
                            }
                            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                    except Exception as e:
                        content = {
                            "message": "Please provide valid data",
                            'error': str(e)
                        }
                        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except Student.DoesNotExist:

                    content = {
                        "message": "invalid invitation ID/ already registered"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                except College.DoesNotExist:

                    content = {
                        "message": "invalid college ID"
                    }
                    return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            else:
                content = {
                    "message": "Please provide valid college admin credentials"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except Exception as e:
            content = {
                "message": "Please provide valid credentials",
                'error': str(e)
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            'message': "invalid request",
            'errors': v.errors
        }
        return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def confirm_registration_payment(request):
    original_order_id = request.POST.get('order_id', None)
    razorpay_payment_id = request.POST.get('razorpay_payment_id', None)
    razorpay_order_id = request.POST.get('razorpay_order_id', None)
    razorpay_signature = request.POST.get('razorpay_signature', None)
    if original_order_id is None or razorpay_payment_id is None or razorpay_order_id is None or razorpay_signature is None:
        content = {
            'response_type': 0,
            'message': 'order id/ razorpay payment id/ razorpay order id/ razorpay signature is required'
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            get_subscription = StudentPaymentDetail.objects.select_related('student').get(
                razorpay_order_id=original_order_id, payment_status=PaymentStatus.INITIATE)

            get_subscription.razorpay_order_id = razorpay_order_id
            get_subscription.razorpay_payment_id = razorpay_payment_id
            get_subscription.razorpay_signature = razorpay_signature
            get_subscription.save()
            params_dict = {
                'original_order_id': get_subscription.razorpay_order_id,
                'razorpay_order_id': get_subscription.razorpay_order_id,
                'razorpay_payment_id': get_subscription.razorpay_payment_id,
                'razorpay_signature': get_subscription.razorpay_signature,
            }
            nm_razorpay_client.utility.verify_payment_signature(params_dict)

            get_subscription.payment_done_at = datetime.now()
            get_subscription.status = PaymentStatus.SUCCESS
            get_subscription.save()
            get_subscription.student.registration_status = StudentRegistrationStatus.PAYMENT_COMPLETE

            get_subscription.student.subscription_status = True
            get_subscription.student.expiry_date = (
                    datetime.now() + timedelta(days=365 * Config.STUDENT_SUBSCRIPTION_YEARS)).date()
            get_subscription.student.save()
            get_subscription.save()

            content = {
                'message': "payment done successful"
            }
            return Response(content, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:

            get_subscription.status = PaymentStatus.FAILED
            get_subscription.save()
            content = {
                'message': "Invalid info"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        except StudentPaymentDetail.DoesNotExist:
            content = {
                'message': "Invalid order id"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def resend_student_invites(request):
    """
    :param request: csv_file

    if -> account_role -> NM admin or NM staff
        1. get list of Students list
            [
                {
                    "invitation_id":"vfdvbfd",
                    "first_name":"student_first_name",
                    "last_name":"student_lst_name",
                    "email":"email",
                    "mobile":"mobile",
                }
            ]
        2. get college record from invitation ID
        3. resend the mails to colleges
    else  -> access Permission error

    :return:
    """
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data['account_role']
    if account_role in [AccountRole.NM_ADMIN, AccountRole.NM_ADMIN_STAFF]:
        try:
            json_data = json.loads(request.body)
            if json_data:
                success_student_count = 0
                failed_students_count = 0
                for record in json_data:
                    try:
                        get_student = Student.objects.get(invitation_id=record['invitation_id'])
                        has_college_update = False
                        if 'first_name' in record:
                            get_student.first_name = record['first_name']
                            has_college_update = True
                        if 'last_name' in record:
                            get_student.last_name = record['last_name']
                            has_college_update = True
                        if 'email' in record:
                            get_student.email = record['email']
                            has_college_update = True
                        if 'mobile' in record:
                            get_student.phone_number = record['mobile']
                            has_college_update = True
                        if has_college_update:
                            get_student.save()
                        try:
                            registration_url = settings.FRONT_END_URL + '/college-registration/' + str(
                                get_student.invitation_id)
                            message = get_template("emails/college_invite.html").render({
                                'registration_url': registration_url
                            })
                            from_email = settings.EMAIL_HOST_FROM
                            mail = EmailMultiAlternatives(
                                "Invitation to Naan Mudhalvan",
                                message,
                                from_email=from_email,
                                to=[get_student.email],
                            )
                            mail.content_subtype = "html"
                            mail.mixed_subtype = 'related'
                            mail.attach_alternative(message, "text/html")
                            send = mail.send()
                            get_student.is_mailed = True
                            get_student.save()
                            success_student_count += 1
                        except Exception as e:
                            print(str(e))
                            failed_students_count += 1

                    except Student.DoesNotExist:
                        failed_students_count += 1

                content = {
                    "message": "Mail send successfully",
                    'success_student_count': success_student_count,
                    'failed_students_count': failed_students_count
                }
                return Response(content, status.HTTP_200_OK, content_type='application/json')

            else:
                content = {
                    "message": "Please provide data"
                }
                return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
        except json.decoder.JSONDecodeError:
            content = {
                "message": "Please provide valid data"
            }
            return Response(content, status.HTTP_400_BAD_REQUEST, content_type='application/json')
    else:
        content = {
            "message": "You dont have the permission"
        }
        return Response(content, status.HTTP_401_UNAUTHORIZED, content_type='application/json')
