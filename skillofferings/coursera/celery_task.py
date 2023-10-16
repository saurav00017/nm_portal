import json

from celery import shared_task
import csv
from io import StringIO
from ..models import SKillOfferingEnrollmentProgress, SKillOffering, SKillOfferingEnrollment, CourseBulkUpload
from student.models import Student
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
import os
@shared_task()
def async_task_coursera_file_upload(coursera_file_upload_id):
    coursera = CourseBulkUpload.objects.get(id=coursera_file_upload_id, course_type=0)
    success_student_ids = []
    invalid_student_ids = []
    invalid_enrollment = []
    failed_student_ids = []
    error_records = []
    try:

        with open(os.path.join(settings.BASE_DIR, "media", coursera.file.name), 'r') as file:
            csv_data = csv.reader(file)
            print(next(csv_data))
            skill_offering_id = coursera.skill_offering_id

            coursera.status = 1
            coursera.save()
            index = 0
            for row in csv_data:
                # if index == 0:
                #     continue
                student_invitation_id = None
                try:
                    student_invitation_id = row[0]
                    try:
                        total_score = float(row[3])
                    except:
                        total_score = 0
                    assessment_data = row[4]
                    try:
                        assessment_data = json.loads(assessment_data)
                    except:
                        assessment_data = None
                    student = Student.objects.get(invitation_id=student_invitation_id)
                    try:
                        skill_offering_enrollment = SKillOfferingEnrollment.objects.get(
                            student_id=student.id,
                            skill_offering_id=skill_offering_id,
                        )
                        try:
                            progress_record = SKillOfferingEnrollmentProgress.objects.get(
                                skill_offering_enrollment_id=skill_offering_enrollment.id
                            )
                        except SKillOfferingEnrollmentProgress.DoesNotExist:
                            progress_record = SKillOfferingEnrollmentProgress.objects.create(
                                skill_offering_enrollment_id=skill_offering_enrollment.id,
                                knowledge_partner_id=coursera.skill_offering.knowledge_partner_id if coursera.skill_offering_id else None
                            )
                        progress_record.progress_percentage = total_score
                        progress_record.assessment_data = assessment_data
                        progress_record.save()
                        success_student_ids.append(student_invitation_id)
                    except SKillOfferingEnrollment.DoesNotExist:
                        invalid_enrollment.append(student_invitation_id)
                except Student.DoesNotExist:
                    invalid_student_ids.append(student_invitation_id)
                except Exception as e:
                    failed_student_ids.append({
                        "record": row,
                        "error": str(e)
                    })

        result_data = {
            'success_student_ids_count': len(success_student_ids),
            'success_student_ids': success_student_ids,
            'invalid_student_ids_count': len(invalid_student_ids),
            'invalid_student_ids': invalid_student_ids,
            'invalid_enrollment_count': len(invalid_enrollment),
            'invalid_enrollment': invalid_enrollment,
            'failed_student_ids_count': len(failed_student_ids),
            'failed_student_ids': failed_student_ids,
            'error_records': error_records,
        }
        coursera.status = 2
        coursera.result_data = result_data
        coursera.save()
        return {"status": True}
    except Exception as e:
        result_data = {
            'success_student_ids_count': len(success_student_ids),
            'success_student_ids': success_student_ids,
            'invalid_student_ids_count': len(invalid_student_ids),
            'invalid_student_ids': invalid_student_ids,
            'invalid_enrollment_count': len(invalid_enrollment),
            'invalid_enrollment': invalid_enrollment,
            'failed_student_ids_count': len(failed_student_ids),
            'failed_student_ids': failed_student_ids,
            'error_records': error_records,
        }
        coursera.status = 3
        coursera.result_data = result_data
        coursera.error_message = str(e)
        return {"status": False, "exception": str(e)}
