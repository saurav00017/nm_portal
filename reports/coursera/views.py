from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress
import csv
from django.http import HttpResponse
from django.utils import timezone
from student.models import Student
from college.models import College
from lms.models import StudentCourse
import pandas as pd
import os
import json
import pandas as pd


@api_view(['POST'])
def generate_coursera_report(request):
    password = request.POST.get('password', None)
    course_serial_file = request.FILES.get('course_serial_file', None)
    membership_file = request.FILES.get('membership_file', None)
    usage_file = request.FILES.get('usage_file', None)
    if password is None or course_serial_file is None or membership_file is None or usage_file is None:
        return Response({"message": "Please provide password/ course_serial_file/ membership_file/ usage_file"}, status=status.HTTP_400_BAD_REQUEST)

    elif password != "password123#":
        return Response({"message": "Please provide valid password"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Course Serial File
        serials_df = pd.read_csv(course_serial_file)
        # print(serials_df.head())
        serials_df.rename(columns={"Coursera Course Name":"Course"}, inplace=True)
        serials_df.rename(columns={"Serial":"serial"}, inplace=True)
        course_names = serials_df['Course']
        course_name_list = course_names.to_list()

        # Membership File
        member_df = pd.read_csv(membership_file)
        enrolled_members_df = member_df[member_df["Member State"] == "MEMBER"]
        final_df = enrolled_members_df[["Email", "External Id", "# Enrolled Courses", "# Completed Courses"]].copy()

        # Usage File
        usage_df = pd.read_csv(usage_file)
        usage_df = usage_df.query(f'Course in {course_name_list}')
        usage_df = pd.merge(usage_df, serials_df, how='inner', on='Course')
        usage_df['attempt'] = 1
        usage_df['score'] = usage_df['Course Grade']
        usage_df['reference'] = usage_df['Course ID']
        student_ids = final_df['External Id']

        final_df['# Enrolled Courses'] = len(course_name_list)

        usage_headers = ['External Id', 'reference', 'score', 'serial', 'attempt']
        usage_limit_df = usage_df[usage_headers]

        for student_id in student_ids:
            usage_records = usage_df[usage_limit_df["External Id"] == student_id].sort_values(by='serial')
            total_score = usage_records.loc[:,"Course Grade"].sum()
            data = usage_records[['serial', 'attempt', 'score', 'reference']]
            json_data = data.to_json(orient="records")
            final_df.loc[final_df['External Id'] == student_id, ['total_sum', 'assessment_data']] = [total_score, json_data]
        final_df['total_score'] = final_df['total_sum']/final_df['# Enrolled Courses']

        response = HttpResponse(content_type='text/csv')
        filename = "coursera_nm_report" + str(timezone.now().strftime("%d-%m-%Y-%H%M%S"))
        response['Content-Disposition'] = f'attachment; filename={filename}.csv'

        csv_headers = ['External Id','# Enrolled Courses', 'total_sum','total_score',  'assessment_data']
        final_df[csv_headers].to_csv(path_or_buf=response, index=False)
        return response

    except Exception as e:
        return Response({"message": "Please provide valid csv file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

import codecs
@api_view(['POST'])
def assessment_status_update(request):
    password = request.POST.get('password', None)
    csv_file = request.FILES.get('csv_file', None)
    if csv_file is None:
        return Response({"message": "Please provide csv_file"}, status=status.HTTP_400_BAD_REQUEST)

    elif password != "password123#":
        return Response({"message": "Please provide valid password"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Course Serial File
        csv_data = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
        error_data = []
        failed_count = 0
        success_count = 0
        for record in csv_data:
            skill_offering_id = record[0]
            email = record[1]
            student_id = record[2]
            assessment_status = record[3]
            completed_status = record[4]

            if str(assessment_status).lower() == 'yes':
                assessment_status = True
            elif str(assessment_status).lower() == 'no':
                assessment_status = False
            else:
                assessment_status = None
            if str(completed_status).lower() == 'yes':
                completed_status = True
            elif str(completed_status).lower() == 'no':
                completed_status = False
            else:
                completed_status = None

            if assessment_status != None or completed_status != None:
                enrollment = SKillOfferingEnrollment.objects.filter(
                    skill_offering_id=skill_offering_id,
                    student__invitation_id=student_id
                ).order_by('-created').first()
                if enrollment:
                    progress = SKillOfferingEnrollmentProgress.objects.filter(
                        skill_offering_enrollment_id=enrollment.id
                    ).order_by('-created').first()
                    if progress:
                        if assessment_status != None:
                            progress.assessment_status=assessment_status
                        if completed_status != None:
                            progress.course_complete=completed_status
                        progress.save()
                        success_count += 1
                    else:
                        error_data.append({
                            'student_id': student_id,
                            'skill_offering_id': skill_offering_id,
                            "error": "No progress"
                        })
                        failed_count += 1

                else:
                    failed_count += 1
                    error_data.append({
                        'student_id': student_id,
                        'skill_offering_id': skill_offering_id,
                        "error": "Not subscribed/ Student not found"
                    })
            else:
                error_data.append({
                    'student_id': student_id,
                    'skill_offering_id': skill_offering_id,
                    "error": "No Assessment/ Completed status"
                })
                failed_count += 1
        return Response(
            {
                "success_count": success_count,
                "failed_count": failed_count,
                'error_data': error_data
             },
            status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": "Please provide valid csv file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

