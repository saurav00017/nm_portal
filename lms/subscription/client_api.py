from ..models import StudentCourse, StudentCourseSubscription
import requests
import json
from django.utils import timezone
import base64
from ..models import LMSDevNames, LmsApiLog
from datarepo.models import CollegeType

def get_api_access_key(lms_client):
    url = str(lms_client.client_base_url) + "token/"
    print(url)
    payload = json.dumps({
        "client_key": str(lms_client.client_key),
        "client_secret": str(lms_client.client_secret)
    })
    headers = {
        'Content-Type': 'application/json',
    }
    print(url)
    print(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    print('--> 1 response', response)
    print('--> 2 response', response.text)
    print('--> 3 response', response.json())

    try:
        data = response.json()
        if 'access_key' in data:
            return True, data['access_key']
        elif "access_token" in data:
            return True, data['access_token']
        elif "token" in data:
            return True, data['token']
        api_log = LmsApiLog.objects.create(
            lms_client_id=lms_client.id,
            payload=payload,
            response=response.text,
            sub_url='token',
            status_code=response.status_code
        )
        return False, None
    except Exception as e:

        api_log = LmsApiLog.objects.create(
            lms_client_id=lms_client.id,
            payload=payload,
            response=str(response.text) + " - " + str(e),
            sub_url='token',
            status_code=response.status_code
        )
        print("get_api_access_key --> Error", e)
        return False, None


def get_class_list_with_key_value(Class):
    items = Class.__dict__.items()
    items = filter(lambda key: not key[0].startswith("_"), items)
    items = dict(items)
    return {v: str(k).replace("_", " ") for k, v in sorted(items.items(), key=lambda item: item[1])}


def get_class_list(Class):
    items = Class.__dict__.items()
    items = filter(lambda key: not key[0].startswith("_"), items)
    items = dict(items)
    return [v for k, v in sorted(items.items(), key=lambda item: item[1])]


def api_subscribe(studentCourse: StudentCourse, only_subscribe=None):
    error_message = None
    lms_client = studentCourse.lms_client
    subscription_status = None
    subscription_reference_id = None
    if lms_client.lms_dev_name is not None:
        if lms_client.lms_dev_name == LMSDevNames.TCS:
            subscription_status = True
        elif lms_client.lms_dev_name == LMSDevNames.CAMBRIDGE:
            student = studentCourse.student
            student_id = studentCourse.student.invitation_id

            institution_types = get_class_list_with_key_value(CollegeType)
            college_type = student.college.college_type if student.college_id else None
            institution_type= None
            if college_type is not None:
                if college_type in institution_types.keys():
                    institution_type = institution_types[college_type]
            if student_id:
                url = "https://naanmudhalvanapi.cambridgeconnect.org/api/students/nmRegister"

                payload = json.dumps({
                    "studentId": str(student_id),
                    "token": "jahsdkashdjaskdjklasjdka",
                    'studentName': student.aadhar_number,
                    'collegeCode': student.college.college_code if student.college_id else None,
                    'collegeName': student.college.college_name if student.college_id else None,
                    'semester': student.sem,
                    'branch': student.rbranch.name if student.rbranch_id else None,
                    'institute': institution_type,
                })
                headers = {
                    'Content-Type': 'application/json',
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                api_log = LmsApiLog.objects.create(
                    lms_client_id=lms_client.id,
                    payload=payload,
                    response=response.text,
                    sub_url='nmRegister',
                    status_code=response.status_code
                )
                print(payload)
                data = response.json()
                print(data)
                if 'status' in data:
                    if data['status'] is 1 or data['status'] is True:
                        subscription_status = True
                    elif 'message' in data:
                        if data['message'] == "User exists with given studentId":
                            subscription_status = True
    else:
        token_status, access_token = get_api_access_key(lms_client=lms_client)
        if token_status:
            url = str(lms_client.client_base_url)+"course/subscribe/"
            print("user_id", studentCourse.student.invitation_id)
            print("course_id", studentCourse.course.course_unique_code)
            payload = json.dumps({
                "user_id": studentCourse.student.invitation_id,
                "course_id": studentCourse.course.course_unique_code
            })
            headers = {
                'Authorization': 'Bearer ' + str(access_token),
                'Content-Type': 'application/json',
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(payload)
            data = response.json()

            print("api_subscribe --> ", response, data)
            print("api_subscribe --> ", response, response.json())

            api_log = LmsApiLog.objects.create(
                lms_client_id=lms_client.id,
                payload=payload,
                response=response.text,
                sub_url='course/subscribe/',
                status_code=response.status_code
            )
            if response.status_code == 200:
                subscription_reference_id = data['subscription_reference_id'] if 'subscription_reference_id' in data else None
                subscription_status = data['subscription_registration_status'] if 'subscription_registration_status' in data else False
            elif response.status_code in [400, 500] and "error" in data:
                error_message = data['error'] if 'error' in data else None
                if error_message in ["Registration already exists",  "Already subscribed"]:
                    subscription_status = True
                    subscription_reference_id = data['subscription_reference_id'] if 'subscription_reference_id' in data else ''
            else:
                error_message = data['error'] if 'error' in data else None
                return subscription_status, error_message

    if subscription_status:
        studentCourse.status = StudentCourseSubscription.SUBSCRIBED_SUCCESS
        studentCourse.subscription_reference_id = subscription_reference_id
        studentCourse.subscription_on = timezone.now()
        if only_subscribe:
            studentCourse.status = StudentCourseSubscription.SUBSCRIBED_SUCCESS
            studentCourse.subscription_reference_id = subscription_reference_id
            studentCourse.subscription_on = timezone.now()
            studentCourse.save()
        else:
            if not StudentCourse.objects.filter(student_id=studentCourse.student_id, course_id=studentCourse.course_id).exists():
                new_subscription = StudentCourse.objects.create(
                    student_id=studentCourse.student_id,
                    course_id=studentCourse.course_id,
                    status=studentCourse.status,
                    subscription_reference_id=studentCourse.subscription_reference_id,
                    subscription_on=studentCourse.subscription_on,
                    lms_client_id=lms_client.id,
                    is_mandatory=studentCourse.is_mandatory
                )
    elif not subscription_status and not studentCourse.subscription_reference_id:
        studentCourse.status = StudentCourseSubscription.SUBSCRIBED_FAILED

    return subscription_status, error_message


from .cambridge_api import get_nm_student_token_for_cambridge

def api_course_watch_url(studentCourse: StudentCourse):
    lms_client = studentCourse.lms_client
    error_message = None
    if lms_client.lms_dev_name is not None:
        lms_dev_name = lms_client.lms_dev_name
        if lms_dev_name == LMSDevNames.TCS:
            first_name = base64.b64encode(bytes(str(studentCourse.student.first_name), 'utf-8'))
            last_name = base64.b64encode(bytes(str(studentCourse.student.last_name), 'utf-8'))
            email = base64.b64encode(bytes(str(studentCourse.student.email), 'utf-8'))
            user_id = base64.b64encode(bytes(str(studentCourse.student.invitation_id), 'utf-8'))
            product_id = base64.b64encode(bytes(str(studentCourse.course.course_unique_code), 'utf-8'))

            access_url = "https://learning.tcsionhub.in//EForms/configuredHtml/1016/78477/application.html?" \
                         "email="+str(email.decode("utf-8"))+"&" \
                                                             "userid="+str(user_id.decode("utf-8"))+"&" \
                                                                                                    "fname="+str(first_name.decode("utf-8"))+"&" \
                                                                                                                                             "lname="+str(last_name.decode("utf-8"))+"&" \
                                                                                                                                                                                     "productid="+str(product_id.decode("utf-8"))
            print('access_url--> ',access_url)
            return True, access_url, error_message
        elif lms_dev_name == LMSDevNames.CAMBRIDGE:
            student_token = get_nm_student_token_for_cambridge(student_id=studentCourse.student.invitation_id)
            access_url = "https://naanmudhalvan.cambridgeconnect.org/dashboard?token=" + str(student_token)
            # print('access_url--> ',access_url)
            return True, access_url, error_message

        return None, None, error_message

    print("\n\nCalling")
    token_status, access_token = get_api_access_key(lms_client=lms_client)

    print("\n\nCalling")
    print(f"token_status: {token_status}\naccess_token: {access_token}")
    if token_status:

        url = str(lms_client.client_base_url)+"course/access/"

        payload = json.dumps({
            "user_id": studentCourse.student.invitation_id,
            "course_id": studentCourse.course.course_unique_code
        })
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        api_log = LmsApiLog.objects.create(
            lms_client_id=lms_client.id,
            payload=payload,
            response=response.text,
            sub_url='course/access/',
            status_code=response.status_code,
        )

        print("\n\npayload", payload)
        print("\n\npayload", response)
        print("\n\npayload", response.text)
        data = response.json()

        print("\n\npayload", payload)
        print("\n\napi_course_watch_url --> ", data)

        access_status = data['access_status'] if 'access_status' in data else None
        if access_status == False:
            lms_subscribe, error_message = api_subscribe(studentCourse, only_subscribe=True)
        access_url = data['access_url'] if 'access_url' in data else None
        error_message = data['error'] if 'error' in data else None
        if error_message:
            error_message = data['message'] if 'message' in data else None

        return access_status, access_url, error_message
    return None, None, error_message

