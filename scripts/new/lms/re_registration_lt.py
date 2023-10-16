from lms.models import StudentCourse
from django.utils import timezone
lms_client_id = 6  # T & L

student_courses = StudentCourse.objects.filter(
    lms_client_id=lms_client_id,
    subscription_on=None
)
print('StudentCourse count', student_courses.count())

access_key = "104150f8e66cae68b40203e1dbba7b4529231970"

for student_course in student_courses:
    try:
        import requests
        import json

        url = "https://users.lntedutech.com/nm/api/course/subscribe"

        payload = json.dumps({
            "user_id": student_course.student.invitation_id,
            "course_id": student_course.course.course_unique_code
        })
        headers = {
            'Authorization': f'Bearer {access_key}',
            'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text, student_course.id)
        data =response.json()
        if data['subscription_registration_status']:
            student_course.subscription_reference_id = data['subscription_reference_id']
            student_course.subscription_on = timezone.now()
            student_course.save()
    except:
        pass


