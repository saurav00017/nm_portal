from lms.models import StudentCourse
from django.utils import timezone
lms_client_id = 20  # skill Lync

student_courses = StudentCourse.objects.filter(
    lms_client_id=lms_client_id,
    course_id=69
)
print('StudentCourse count', student_courses.count())

access_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnQiOiJ0bnNkYyIsImNsaWVudF9rZXkiOiJZMlpsTVdJek1tTTNOakUyTldFMk5UQTJaRGd3TnpSaU16TmpNREl6WXpBMVpXUm1aV0UyTkNBZ0xRbyIsImV4cGlyeSI6MTY2NjE3MjQ5MX0.bYCI_k0xtfOCoDcVyd8qlXCXkfXxnHYfhVSXywNDJXo"

for student_course in student_courses:
    try:
        import requests
        import json

        url = "https://naanmudhalvan.skill-lync.com/api/v1/course/subscribe"

        payload = json.dumps({
            "user_id": student_course.student.invitation_id,
            "course_id": student_course.course.course_unique_code
        })
        headers = {
            'Authorization': f'Bearer {access_key}',
            'Content-Type': 'application/json',
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text, student_course.id)
        data =response.json()
        if data['subscription_registration_status']:
            student_course.subscription_reference_id = data['subscription_reference_id']
            student_course.subscription_on = timezone.now()
            student_course.save()
    except:
        pass

