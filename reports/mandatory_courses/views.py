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
import pandas as pd
import os
import json


@api_view(['POST'])
def mandatory_courses_report(request):
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

    mandatory_courses_list = MandatoryCourse.objects.select_related('college', 'skill_offering', 'branch').filter(
        college__college_code__in=college_code_list).order_by(
        'college__college_code',
        'branch_id',
        'sem',
    )
    response = HttpResponse(content_type='text/csv')
    filename = "mandatory_course_report_" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
    response['Content-Disposition'] = f'attachment; filename={filename}.csv'
    writer = csv.writer(response)
    headers = ['college_code', 'branch', 'sem', 'course', 'allocate_count', 'enrolled count', 'total_students', 'course type', 'is unlimited']
    writer.writerow(headers)

    for md_course in mandatory_courses_list:

        course_type = None
        if md_course.course_type == 0:
            course_type = 'Free'
        elif md_course.course_type == 1:
            course_type = 'Paid'
        enrolled_count = SKillOfferingEnrollment.objects.select_related('student').filter(
            student__college_id=md_course.college_id,
            student__rbranch_id=md_course.branch_id,
            student__sem=md_course.sem, skill_offering_id=md_course.skill_offering_id).count()

        total_students_count = Student.objects.filter(college_id=md_course.college_id,
                                                      rbranch_id=md_course.branch_id,
                                                      sem=md_course.sem
                                                      ).count(),
        writer.writerow([
            md_course.college.college_code if md_course.college_id else None,
            md_course.branch.name if md_course.branch_id else None,
            md_course.sem,
            md_course.skill_offering.course_name if md_course.skill_offering_id else None,
            # allocate_count
            md_course.count,
            enrolled_count,
            total_students_count,
            # course type
            course_type,
            md_course.is_unlimited

        ])
    return response



@api_view(['POST'])
def mandatory_course_with_student_report(request):
    password = request.POST.get('password', None)
    file = request.FILES.get('file', None)
    if password is None or file is None:
        return Response({"message": "Please provide password/ file"}, status=status.HTTP_400_BAD_REQUEST)

    elif password != "password123#":
        return Response({"message": "Please provide valid password"}, status=status.HTTP_400_BAD_REQUEST)
    college_code_list = []

    final_data = []
    headers = ["College code", "Branch code", "Sem", "Course code", "Number of allocations", "Course type", "Unlimited"]
    try:
        file_data = file.read().decode('utf-8')
        file_data = str(file_data).split("\n")
        for record in file_data:
            college_code = str(record).replace("\t", "").replace("\r", "")
            try:
                get_college = College.objects.get(college_code=college_code)
                mandatory_courses_list = MandatoryCourse.objects.filter(college_id=get_college.id)

                for mandatory_course in mandatory_courses_list:
                    course_type = None
                    if mandatory_course.course_type == 0:
                        course_type = 'Free'
                    elif mandatory_course.course_type == 1:
                        course_type = 'Paid'
                    final_data.append([
                        college_code,
                        mandatory_course.branch_id,
                        mandatory_course.sem,
                        mandatory_course.count,
                        course_type,
                        "yes" if mandatory_course.is_unlimited else "no"
                    ])
            except:
                pass
        response = HttpResponse(content_type='text/csv')
        filename = "mandatory_course_report_" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
        response['Content-Disposition'] = f'attachment; filename={filename}.csv'
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(final_data)
        return response

    except Exception as e:
        return Response({"message": "Please provide valid csv file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_mandatory_courses(request):
    password = request.POST.get('password', None)
    file = request.FILES.get('file', None)
    if password is None or file is None:
        return Response({"message": "Please provide password/ file"}, status=status.HTTP_400_BAD_REQUEST)

    elif password != "password123#":
        return Response({"message": "Please provide valid password"}, status=status.HTTP_400_BAD_REQUEST)
    college_code_list = []

    updated_records_count = 0
    new_records_count = 0
    try:
        file_data = file.read().decode('utf-8')
        file_data = str(file_data).split("\n")
        for record in file_data:
            record = str(record).replace("\t", "").replace("\r", "")
            record = str(record).split(",")
            """
            0 College Code,
            1 Branch code,
            2 Sem,
            3. course code,
            4 Number of allocations,
            5 Course type,
            6 Unlimited 
            """
            college_code = record[0]
            branch_id = record[1]
            sem = record[2]
            course_code = record[3]
            allocation_count = record[4]
            _course_type = record[5]
            is_unlimited = record[6]

            course_type = None
            if str(_course_type).lower().strip() == "free":
                course_type = 0
            elif str(_course_type).lower().strip() == "paid":
                course_type = 1
            is_unlimited = True if str(is_unlimited).lower().strip() == "yes" else False
            try:
                get_college = College.objects.get(college_code=college_code)
                get_mandatory = MandatoryCourse.objects.get(
                    college_id=get_college.id,
                    branch_id=branch_id,
                    sem=sem,
                    skill_offering_id=course_code
                )
                get_mandatory.count=allocation_count
                get_mandatory.course_type = course_type
                get_mandatory.is_unlimited = is_unlimited
                get_mandatory.save()
                updated_records_count += 1
            except MandatoryCourse.DoesNotExist:
                get_mandatory = MandatoryCourse.objects.create(
                    college_id=get_college.id,
                    branch_id=branch_id,
                    sem=sem,
                    skill_offering_id=course_code,
                    count=allocation_count,
                    course_type=course_type,
                    is_unlimited=is_unlimited
                )
                get_mandatory.save()
                new_records_count += 1
            except Exception as e:
                print("Error", e)
        context = {
            'updated_records_count': updated_records_count,
            'new_records_count': new_records_count
        }
        return Response(context, status=status.HTTP_200_OK)
        # response = HttpResponse(content_type='text/csv')
        # filename = "mandatory_course_report_" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
        # response['Content-Disposition'] = f'attachment; filename={filename}.csv'
        # writer = csv.writer(response)
        # writer.writerow(headers)
        # writer.writerows(final_data)
        # return response

    except Exception as e:
        return Response({"message": "Please provide valid csv file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def student_mandatory_courses(request):
    password = request.POST.get('password', None)
    file = request.FILES.get('file', None)
    if password is None or file is None:
        return Response({"message": "Please provide password/ file"}, status=status.HTTP_400_BAD_REQUEST)

    elif password != "password123#":
        return Response({"message": "Please provide valid password"}, status=status.HTTP_400_BAD_REQUEST)
    college_code_list = []

    try:
        headers = ['college code', 'college name', 'branch','sem','invitation_id', 'roll_no', 'email', 'course_name', 'kp_name', 'created','updated','percentage',]
        final_records = []

        total_zone_1_allocations = 0
        enrollment_count = 0
        sub_count = 0
        dup_sub = 0

        file_data = file.read().decode('utf-8')
        csv_data = str(file_data).split("\n")
        for record in csv_data:
            college_code = record[0]
            try:
                college_info = College.objects.get(college_code=college_code)
                mandatory_branches = MandatoryCourse.objects.filter(college_id=college_info.id).distinct('branch_id')
                mandatory_sems = list(mandatory_branches.distinct('sem').values('sem'))
                for branch in mandatory_branches:
                    for sem in mandatory_sems:
                        print(branch.id,sem['sem'])
                        b_s_students = Student.objects.filter(sem=sem['sem'],rbranch_id=branch.branch.id,college_id=college_info.id)
                        for student in b_s_students:
                            try:
                                check_sf_e = SKillOfferingEnrollment.objects.get(student_id=student.id,is_mandatory=1)
                                enrollment_count = enrollment_count + 1
                                try:
                                    subscription = StudentCourse.objects.get(student_id=student.id,course_id=check_sf_e.skill_offering.lms_course_id,status=1)
                                    if subscription:
                                        sub_count = sub_count + 1
                                        data = [college_info.college_code,college_info.college_name,student.rbranch.name,student.sem,student.invitation_id,student.roll_no,student.email,check_sf_e.skill_offering.course_name,check_sf_e.knowledge_partner.name,subscription.created,subscription.updated,subscription.progress_percentage]
                                        final_records.append(data)
                                except StudentCourse.DoesNotExist:
                                    pass
                                except StudentCourse.MultipleObjectsReturned:
                                    sub_count = sub_count + 1
                                    subscriptions = StudentCourse.objects.filter(student_id=student.id,course_id=check_sf_e.skill_offering.lms_course_id,status=1)
                                    dup_sub = dup_sub + subscriptions.count()
                                print(sub_count)
                                print(dup_sub)
                            except SKillOfferingEnrollment.DoesNotExist:
                                pass
            except College.DoesNotExist:
                print("college missed----------------------------------------")

        response = HttpResponse(content_type='text/csv')
        filename = "mandatory_course_report_" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
        response['Content-Disposition'] = f'attachment; filename={filename}.csv'
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(final_records)
        return response
    except Exception as e:
        return Response({"message": "Please provide valid csv file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


