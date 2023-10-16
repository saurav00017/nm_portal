import json

from celery import shared_task
import csv
from io import StringIO
from ..models import SKillOfferingEnrollmentProgress, SKillOffering, SKillOfferingEnrollment, CourseBulkUpload
from student.models import Student
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
import os
from django.utils import timezone
@shared_task()
def async_task_microsoft_file_upload(course_file_upload_id, serial):
    course_file_record = CourseBulkUpload.objects.get(id=course_file_upload_id, course_type=1)
    student_not_found_count = 0
    success_student_count = 0
    failed_student_count = 0
    student_not_found_data = []
    enrollment_not_found_data = []
    enrollment_not_found_count = 0
    invalid_score = 0
    invalid_score_count = 0
    invalid_score_data = []
    try:
        with open(os.path.join(settings.BASE_DIR, "media", course_file_record.file.name), 'r') as file:
            csv_data = csv.reader(file)
            print(next(csv_data))
            skill_offering_id = course_file_record.skill_offering_id

            course_file_record.status = 1
            course_file_record.save()
            index = 0
            for row in csv_data:
                print(type(row), len(row),row)
                """
                0 Course	
                1 Contact	
                2 Name	
                3 Lessons Completed	
                4 Quizzes Completed	
                5 Course Completion Percentage	
                6 Average Score
                """
                # """
                # 0 - Phone Number
                # 1 - First Name
                # 2 - Last Name
                # 3 - CourseCompletionPercentage
                # 4 - CoursesCompleted
                # 5 - AverageAssessmentScore
                # 6 - CoursesRegistered
                # 8 - CertificatesReceived
                # """
                internal_assessment_count = None
                phone_number = row[1]
                try:
                    score = float(row[6])
                except:

                    print(f"SKillOfferingEnrollment.DoesNotExist - {phone_number}")
                    invalid_score_count += 0
                    invalid_score_data.append({
                        "phone_number": phone_number
                    })
                    failed_student_count += 1
                    continue

                data_record = {
                    "score": score,
                    "serial": serial,
                    "attempt": "1",
                    "created": None,
                    "updated": None,
                    "reference": None,
                    "total_questions": None,
                    "correct_answers": None,
                    "submitted_on": timezone.now().strftime("%Y-%m-%d %H:%M%S")
                }

                if phone_number:
                    phone_number = str(phone_number).replace("+91 ", "")
                    try:
                        student = Student.objects.get(phone_number=phone_number)
                        try:
                            try:
                                skill_offering_enrollment = SKillOfferingEnrollment.objects.get(student_id=student.id, skill_offering_id=course_file_record.skill_offering_id)
                            except SKillOfferingEnrollment.MultipleObjectsReturned:
                                skill_offering_enrollment = SKillOfferingEnrollment.objects.filter(student_id=student.id, skill_offering_id=course_file_record.skill_offering_id
                                                                                                   ).order_by('-created').first()
                            internal_assessment_count = skill_offering_enrollment.skill_offering.ia_count if skill_offering_enrollment.skill_offering_id else None
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
                            if progress_record.assessment_data:
                                assessment_data = progress_record.assessment_data
                                if isinstance(assessment_data, list):
                                    same_serial_records = list(filter(lambda x: x['serial'] == serial, assessment_data))
                                    for record in same_serial_records:
                                        assessment_data.remove(record)
                                    assessment_data.append(data_record)
                                else:
                                    assessment_data = [data_record]

                            else:
                                assessment_data = [data_record]
                            total_sum_scores = sum(list(map(lambda x: x['score'], assessment_data)))
                            if internal_assessment_count:
                                progress_record.progress_percentage = total_sum_scores / internal_assessment_count

                            progress_record.assessment_data = assessment_data
                            progress_record.save()
                            success_student_count += 1

                            print(f"progress_record - {phone_number} - {serial} | {total_sum_scores}")
                        except SKillOfferingEnrollment.DoesNotExist:
                            print(f"SKillOfferingEnrollment.DoesNotExist - {phone_number}")
                            enrollment_not_found_count += 0
                            enrollment_not_found_data.append({
                                "phone_number": phone_number
                            })
                            failed_student_count += 1
                    except Student.MultipleObjectsReturned:
                        students_list = Student.objects.filter(phone_number=phone_number).order_by('created')
                        for student in students_list:
                            try:
                                try:
                                    skill_offering_enrollment = SKillOfferingEnrollment.objects.get(student_id=student.id, skill_offering_id=course_file_record.skill_offering_id)
                                except SKillOfferingEnrollment.MultipleObjectsReturned:
                                    skill_offering_enrollment = SKillOfferingEnrollment.objects.filter(student_id=student.id, skill_offering_id=course_file_record.skill_offering_id
                                                                                                       ).order_by('-created').first()
                                internal_assessment_count = skill_offering_enrollment.skill_offering.ia_count if skill_offering_enrollment.skill_offering_id else None
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
                                if progress_record.assessment_data:
                                    assessment_data = progress_record.assessment_data
                                    if isinstance(assessment_data, list):
                                        same_serial_records = list(filter(lambda x: x['serial'] == serial, assessment_data))
                                        for record in same_serial_records:
                                            assessment_data.remove(record)
                                        assessment_data.append(data_record)
                                    else:
                                        assessment_data = [data_record]

                                else:
                                    assessment_data = [data_record]
                                total_sum_scores = sum(list(map(lambda x: x['score'], assessment_data)))
                                if internal_assessment_count:
                                    progress_record.progress_percentage = total_sum_scores / internal_assessment_count

                                progress_record.assessment_data = assessment_data
                                progress_record.save()
                                success_student_count += 1

                                print(f"progress_record - {phone_number} - {serial} | {total_sum_scores}")

                            except SKillOfferingEnrollment.DoesNotExist:
                                print(f"SKillOfferingEnrollment.DoesNotExist - {phone_number}")
                                enrollment_not_found_count += 0
                                enrollment_not_found_data.append({
                                    "phone_number": phone_number
                                })
                                failed_student_count += 1

                    except Student.DoesNotExist:
                        student_not_found_count += 0
                        student_not_found_data.append({
                            "phone_number": phone_number
                        })
                        failed_student_count += 1
                        print(f"student_not_found_data - {phone_number}")
                        continue

        result_data = {
            'success_student_count': success_student_count,
            'student_not_found_count': student_not_found_count,
            'failed_student_count': failed_student_count,
            'student_not_found_data': student_not_found_data,
            'enrollment_not_found_count': enrollment_not_found_count,
            'enrollment_not_found_data': enrollment_not_found_data,
        }
        course_file_record.status = 2
        course_file_record.result_data = result_data
        course_file_record.save()
        return {"status": True}
    except Exception as e:
        result_data = {
            'serial': serial,
            'success_student_count': success_student_count,
            'student_not_found_count': student_not_found_count,
            'failed_student_count': failed_student_count,
            'student_not_found_data': student_not_found_data,
            'enrollment_not_found_count': enrollment_not_found_count,
            'enrollment_not_found_data': enrollment_not_found_data,
        }
        course_file_record.status = 3
        course_file_record.result_data = result_data
        course_file_record.error_message = str(e)
        course_file_record.save()
        return {"status": False, "exception": str(e)}
