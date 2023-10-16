from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
from django.http import HttpResponse
from django.utils import timezone
from student.models import Student
from college.models import College
from lms.models import StudentCourse


@api_view(['POST'])
def list_college_report(request):
    password = request.POST.get('password', None)
    file = request.FILES.get('file', None)
    if password is None or file is None:
        return Response({"message": "Please provide password/ file"}, status=status.HTTP_400_BAD_REQUEST)

    elif password != "password123#":
        return Response({"message": "Please provide valid password"}, status=status.HTTP_400_BAD_REQUEST)
    college_code_list = []

    try:

        data = file.read().decode('utf-8')
        data = str(data).split("\n")
        for record in data:
            record = str(record).replace("\t", "").replace("\r", "")
            college_code_list.append(record)
    except Exception as e:
        return Response({"message": "Please provide valid csv file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    college_list = College.objects.filter(college_code__in=college_code_list)
    response = HttpResponse(content_type='text/csv')
    filename = "mandatory_course_report_" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
    response['Content-Disposition'] = f'attachment; filename={filename}.csv'
    writer = csv.writer(response)
    headers = [
        'college_code',
        'college name',
        'email',
        'phone number',
        'no of students',
        'students enrollment for mandatory course',
        'students allocated',
        'finished allocation'
    ]
    writer.writerow(headers)

    for clg in college_list:
        total_students_count = Student.objects.filter(college_id=clg.id).count()
        md_courses_list = MandatoryCourse.objects.filter(college_id=clg.id)
        skill_offering_ids = md_courses_list.values_list('skill_offering_id', flat=True)
        students_allocated_count = SKillOfferingEnrollment.objects.filter(
            student__college_id=clg.id,
            skill_offering_id__in=skill_offering_ids

        ).count()
        if MandatoryCourse.objects.filter(college_id=clg.id, is_unlimited=True).exists():
            enrollment_for_mandatory_course_count = total_students_count
        else:
            enrollment_for_mandatory_course_count = 0
            for md_course in md_courses_list:
                enrollment_for_mandatory_course_count += md_course.count
        writer.writerow([
            # 'college_code',
            clg.college_code,
            # 'college name',
            clg.college_name,
            # 'email',
            clg.email,
            # 'phone number'
            clg.mobile,
            # 'no of students',
            total_students_count,
            # 'students enrollment for mandatory course',
            enrollment_for_mandatory_course_count,
            # 'students allocated',
            students_allocated_count,
            # 'finish allocation'
            "Yes" if clg.course_allocation == 1 else "No"
        ])
    return response

