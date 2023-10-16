from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from ..models import Specialisation, SKillOffering, SKillOfferingEnrollment, SKillOfferingEnrollmentProgress, Technology, \
    SubTechnology, MandatoryCourse, FeedBack
from django.db.models import Count
import csv
from io import StringIO
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import jwt
from users.models import User, AccountRole, UserDetail

from django.conf import settings
from student.models import Student
from datarepo.models import Branch, YearOfStudy
from lms.models import Course as LMSCourse
from kp.models import KnowledgePartner
import math
from cerberus import Validator
import yaml
import jwt

from django.db import transaction as atomic_transaction


@api_view(['GET', 'POST'])
@authentication_classes([JWTTokenUserAuthentication])
@permission_classes([IsAuthenticated])
def feed_back(request):
    token = request.headers['Authorization']
    decoded_data = jwt.decode(token[7:], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    account_role = decoded_data.get('account_role', None)

    if account_role == AccountRole.STUDENT:
        try:
            user_details = UserDetail.objects.get(user_id=request.user.id)
            student = user_details.student
            if request.method == 'POST':
                enrollment_id = request.POST.get('enrollment_id', None)
                quality_of_course = request.POST.get('quality_of_course', None)
                quality_of_trainer = request.POST.get('quality_of_trainer', None)
                has_the_course_increased_your_motivation_to_upskill = request.POST.get('has_the_course_increased_your_motivation_to_upskill', None)
                did_you_have_supportive_teachers_who_could_help_with_queries = request.POST.get('did_you_have_supportive_teachers_who_could_help_with_queries', None)
                time_allocated_to_you_for_the_training_and_homework_sufficient = request.POST.get('time_allocated_to_you_for_the_training_and_homework_sufficient', None)
                doubt_clearing_sessions_held_by_the_trainer = request.POST.get('doubt_clearing_sessions_held_by_the_trainer', None)
                is_hybrid_training_more_effective = request.POST.get('is_hybrid_training_more_effective', None)
                training_sufficient_with_days = request.POST.get('training_sufficient_with_days', None)
                interested_in_working_in_large_projects = request.POST.get('interested_in_working_in_large_projects', None)
                repeat_the_training = request.POST.get('repeat_the_training', None)
                enjoyment_in_course = request.POST.get('enjoyment_in_course', None)
                course_like_to_take = request.POST.get('course_like_to_take', None)
                doubts_get_cleared = request.POST.get('doubts_get_cleared', None)

                if not enrollment_id:
                    # try:
                    enrollment = SKillOfferingEnrollment.objects.values('id').filter(is_mandatory=True, student_id=user_details.student_id).order_by('created').last()
                    if not enrollment:
                        return Response({'message': 'Please enroll the course'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    else:
                        enrollment_id = enrollment['id']
                try:
                    enrollment = SKillOfferingEnrollment.objects.get(id=enrollment_id, student_id=user_details.student_id)
                    try:
                        feed_back_record = FeedBack.objects.get(student_id=user_details.student_id, enrollment_id=enrollment_id)
                        return Response({'message': 'Feedback already submitted'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
                    except FeedBack.DoesNotExist:
                        try:
                            progress_record = SKillOfferingEnrollmentProgress.objects.get(skill_offering_enrollment_id=enrollment.id)
                        except SKillOfferingEnrollmentProgress.DoesNotExist:

                            progress_record = SKillOfferingEnrollmentProgress.objects.create(
                                knowledge_partner_id=enrollment.skill_offering.knowledge_partner_id if enrollment.skill_offering_id else None,
                            skill_offering_enrollment_id=enrollment.id)

                        new_feed_back = FeedBack.objects.create(
                            student_id=user_details.student_id,
                            enrollment_id=enrollment.id,
                            skill_offering_id=enrollment.skill_offering_id,
                            course_name=enrollment.skill_offering.course_name if enrollment.skill_offering_id else None,
                            course_code=enrollment.skill_offering.course_code if enrollment.skill_offering_id else None,
                            quality_of_course=quality_of_course,
                            quality_of_trainer=quality_of_trainer,
                            has_the_course_increased_your_motivation_to_upskill=has_the_course_increased_your_motivation_to_upskill,
                            did_you_have_supportive_teachers_who_could_help_with_queries=did_you_have_supportive_teachers_who_could_help_with_queries,
                            time_allocated_to_you_for_the_training_and_homework_sufficient=time_allocated_to_you_for_the_training_and_homework_sufficient,
                            doubt_clearing_sessions_held_by_the_trainer=doubt_clearing_sessions_held_by_the_trainer,
                            doubts_get_cleared=doubts_get_cleared,
                            is_hybrid_training_more_effective=is_hybrid_training_more_effective,
                            training_sufficient_with_days=training_sufficient_with_days,
                            interested_in_working_in_large_projects=interested_in_working_in_large_projects,
                            repeat_the_training=repeat_the_training,
                            enjoyment_in_course=enjoyment_in_course,
                            course_like_to_take=course_like_to_take,
                        )
                        progress_record.feedback_status = True
                        progress_record.save()
                        return Response({'message': 'Updated successfully'}, status.HTTP_200_OK, content_type='application/json')
                except SKillOfferingEnrollment.DoesNotExist:
                    return Response({'message': 'Please provide valid enrollment_id'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')
            elif request.method == 'GET':
                enrollment_id = request.GET.get('enrollment_id', None)
                if not enrollment_id:
                    return Response({'message': 'Please provide enrollment_id'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                try:
                    enrollment = SKillOfferingEnrollment.objects.get(id=enrollment_id, student_id=user_details.student_id)
                    try:
                        try:
                            feedback_record = FeedBack.objects.get(enrollment_id=enrollment_id, student_id=user_details.student_id)
                        except FeedBack.DoesNotExist:
                            feedback_record = None

                        context = {
                            'feedback_id': feedback_record.id if feedback_record else None,
                            'enrollment_id': enrollment.id,
                            'skill_offering_id': enrollment.skill_offering_id,
                            'course_name': enrollment.skill_offering.course_name if enrollment.skill_offering_id else None,
                            'course_code': enrollment.skill_offering.course_name if enrollment.skill_offering_id else None,
                            'quality_of_course': feedback_record.quality_of_course if feedback_record else None,
                            'quality_of_trainer': feedback_record.quality_of_trainer if feedback_record else None,
                            'has_the_course_increased_your_motivation_to_upskill': feedback_record.has_the_course_increased_your_motivation_to_upskill if feedback_record else None,
                            'did_you_have_supportive_teachers_who_could_help_with_queries': feedback_record.did_you_have_supportive_teachers_who_could_help_with_queries if feedback_record else None,
                            'time_allocated_to_you_for_the_training_and_homework_sufficient': feedback_record.time_allocated_to_you_for_the_training_and_homework_sufficient if feedback_record else None,
                            'doubt_clearing_sessions_held_by_the_trainer': feedback_record.doubt_clearing_sessions_held_by_the_trainer if feedback_record else None,
                            'doubts_get_cleared': feedback_record.doubts_get_cleared if feedback_record else None,
                            'is_hybrid_training_more_effective': feedback_record.is_hybrid_training_more_effective if feedback_record else None,
                            'training_sufficient_with_days': feedback_record.training_sufficient_with_days if feedback_record else None,
                            'interested_in_working_in_large_projects': feedback_record.interested_in_working_in_large_projects if feedback_record else None,
                            'repeat_the_training': feedback_record.repeat_the_training if feedback_record else None,
                            'enjoyment_in_course': feedback_record.enjoyment_in_course if feedback_record else None,
                            'course_like_to_take': feedback_record.course_like_to_take if feedback_record else None,
                            'created': feedback_record.created if feedback_record else None,
                            'updated': feedback_record.updated if feedback_record else None,

                        }
                        return Response(context, status.HTTP_200_OK, content_type='application/json')
                    except FeedBack.DoesNotExist:
                        return Response({'message': 'Feedback need to be submit'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

                except SKillOfferingEnrollment.objects.DoesNotExist:
                    return Response({'message': 'Please provide valid enrollment_id'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

        except UserDetail.DoesNotExist:

            return Response({'message': 'Please contact admin'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

    return Response({'message': 'You dont have the permission'}, status.HTTP_400_BAD_REQUEST, content_type='application/json')

