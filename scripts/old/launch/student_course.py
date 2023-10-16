from lms.models import StudentCourse
from django.db import IntegrityError, transaction
student_courses = StudentCourse.objects.distinct('student_id', 'course_id')

counter = student_courses.count()
index = 0

for record in student_courses:
    index += 1
    if StudentCourse.objects.filter(
            student_id=record.student_id,
            course_id=record.course_id).count() > 1:
        with transaction.atomic():
            records = StudentCourse.objects.select_for_update().filter(
                student_id=record.student_id,
                course_id=record.course_id).order_by('-created')
            record = records.first()

            data_records = records.exclude(id=record.id)
            for sub in data_records:
                sub.delete()
    else:
        print(False)
    print("Pending", counter-index)
