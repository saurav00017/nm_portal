import json

from celery import shared_task
import csv
from io import StringIO
from ..models import SKillOfferingEnrollmentProgress, SKillOffering, SKillOfferingEnrollment, CourseBulkUpload
from student.models import Student
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
import os
import pandas as pd
from django.utils import timezone

@shared_task()
def async_task_infosys_file_upload(course_file_upload_id):
    student_not_found_count = 0
    success_student_count = 0
    failed_student_count = 0
    student_not_found_data = []
    student_more_than_one_count = 0
    student_more_than_one_data = []
    enrollment_not_found_data = []
    enrollment_not_found_count = 0
    exception_student_count = 0
    exception_student_data = []
    invalid_score = 0
    invalid_score_count = 0
    invalid_score_data = []
    course_file_record = CourseBulkUpload.objects.get(id=course_file_upload_id)
    try:
        # Serial Data
        serial_df = pd.read_csv(os.path.join(settings.BASE_DIR, "skillofferings/infosys", 'infosys_serials.csv'))
        serial_df =serial_df[['Assessment ID', 'Course ID', 'Serial']].set_index('Assessment ID')
        # Student Data
        with open(os.path.join(settings.BASE_DIR, "media", course_file_record.file.name), 'r') as file:
            df = pd.read_csv(file)
            students_emails = df["Email"].unique()
            df = pd.merge(df, serial_df, left_on="Assessment Id", right_on="Assessment ID")
            # df = df
            final_list = []
            total = len(students_emails)
            fail_student_records = []
            index = 0
            for email in students_emails:
                index += 1
                print("Pending --> ", total-index)
                try:
                    students_list = Student.objects.get(email__iexact=email)
                    if students_list:
                        for student in students_list:
                            skill_offering_enrollment = SKillOfferingEnrollment.objects.get(student_id=student.id, skill_offering_id__in=[2221,2222,2223,2224])
                            internal_assessment_count = skill_offering_enrollment.skill_offering.ia_count if skill_offering_enrollment.skill_offering_id else None
                            course_name = skill_offering_enrollment.skill_offering.course_name
                            course_code = skill_offering_enrollment.skill_offering.course_code
                            try:
                                progress_record = SKillOfferingEnrollmentProgress.objects.get(
                                    skill_offering_enrollment_id=skill_offering_enrollment.id
                                )

                            except SKillOfferingEnrollmentProgress.MultipleObjectsReturned:
                                progress_record = SKillOfferingEnrollmentProgress.objects.filter(
                                    skill_offering_enrollment_id=skill_offering_enrollment.id
                                ).order_by('-created').first()
                            except SKillOfferingEnrollmentProgress.DoesNotExist:
                                progress_record = SKillOfferingEnrollmentProgress.objects.create(
                                    skill_offering_enrollment_id=skill_offering_enrollment.id,
                                    knowledge_partner_id=course_file_record.skill_offering.knowledge_partner_id if course_file_record.skill_offering_id else None
                                )

                            try:
                                print("Flag 1")
                                # Course ID from Skill offering
                                course_id = skill_offering_enrollment.skill_offering.course_code
                                # list of assessments with filter email & course
                                student_df = df[(df['Email'] == email) & (df['Course ID'] == course_id)]
                                print("Flag 1.1")

                                course_assessments_df = serial_df[serial_df['Course ID'] == course_id]
                                assessments = course_assessments_df.index.values.tolist()
                                # try:
                                #     assessments = course_assessments_df['Assessment Id'].unique()
                                # except:
                                #     assessments = [course_assessments_df['Assessment Id']]
                                #     if assessments:
                                #         assessments = list(set(assessments))

                                print("Flag 2")
                                assessments_count = len(assessments)
                                temp = {"email": email, 'assessments_count': assessments_count}
                                assessment_data = []
                                total_score = 0

                                print("Flag 3")
                                course_assessments_df = serial_df[serial_df['Course ID'] == course_id]

                                print("Flag 4")
                                for assessment in assessments:
                                    print("Loop Flag 1")
                                    max_score = student_df[student_df['Assessment Id'] == assessment]["Marks Obtained"].max()
                                    print("Loop Flag 2")
                                    if str(max_score) != "nan":
                                        serial = course_assessments_df.loc[assessment]['Serial']
                                        total_score += max_score
                                        print("Loop Flag 3")
                                        temp_assessment = {
                                            'score': max_score,
                                            "attempt": 1,
                                            "serial":str(serial),
                                            'reference': assessment,
                                            'total_questions': 0,
                                            'correct_answers': 0,
                                            "created": None,
                                            'updated': None,
                                            "submitted_on": timezone.now().strftime("%Y-%m-%d %H:%M%S")
                                        }
                                        assessment_data.append(temp_assessment)
                                print(f"-->{total_score} - {internal_assessment_count}")
                                print(f"assessments_count : {assessments_count}")
                                print(f"internal_assessment_count : {internal_assessment_count} - {email} - {course_name} - {course_code}")
                                # temp['total_sum'] = total_score
                                # temp['total_score'] = total_score/assessments_count
                                # temp['assessment_data'] = json.dumps(assessment_data)
                                # final_list.append(temp)

                                progress_record.progress_percentage = total_score / internal_assessment_count
                                progress_record.assessment_data = assessment_data
                                progress_record.save()
                                print(f"{email} - {progress_record.id}")
                                success_student_count += 1
                            except Exception as e:
                                fail_student_records.append(f"{email}-{student.invitation_id}")
                                print("error", e, email)

                            except SKillOfferingEnrollment.DoesNotExist:

                                print(f"SKillOfferingEnrollment.DoesNotExist - {email}")
                                enrollment_not_found_count += 0
                                enrollment_not_found_data.append({
                                    "email": email,
                                    "student_id": student.invitation_id
                                })
                                failed_student_count += 1

                    else:
                        failed_student_count += 1
                        student_not_found_data.append(email)

                except Student.DoesNotExist:
                    failed_student_count += 1
                    student_not_found_data.append(email)
                except Student.MultipleObjectsReturned:
                    failed_student_count += 1
                    student_more_than_one_count += 1
                    student_more_than_one_data.append(email)
                except Exception as e:
                    failed_student_count += 1
                    exception_student_count += 1
                    exception_student_data.append(email)

        result_data = {
            'success_student_count': success_student_count,
            'student_not_found_count': student_not_found_count,
            'failed_student_count': failed_student_count,
            'student_not_found_data': student_not_found_data,
            'enrollment_not_found_count': enrollment_not_found_count,
            'enrollment_not_found_data': enrollment_not_found_data,
            'exception_student_count': exception_student_count,
            'exception_student_data': exception_student_data,
            "student_more_than_one_count": student_more_than_one_count,
            "student_more_than_one_data": student_more_than_one_data,

        }
        course_file_record.status = 2
        course_file_record.result_data = result_data
        course_file_record.save()
        return {"status": True}
    except Exception as e:
        result_data = {
            'serial': 'serial',
            'success_student_count': success_student_count,
            'student_not_found_count': student_not_found_count,
            'failed_student_count': failed_student_count,
            'student_not_found_data': student_not_found_data,
            'enrollment_not_found_count': enrollment_not_found_count,
            'enrollment_not_found_data': enrollment_not_found_data,
            'exception_student_count': exception_student_count,
            'exception_student_data': exception_student_data,
            "student_more_than_one_count": student_more_than_one_count,
            "student_more_than_one_data": student_more_than_one_data,
        }
        course_file_record.status = 3
        course_file_record.result_data = result_data
        course_file_record.error_message = str(e)
        course_file_record.save()
        return {"status": False, "exception": str(e)}
