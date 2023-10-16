from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv
import os
from django.conf import settings
from lms.models import StudentCourse
import collections


header = ['id', 'student', 'student_name' 'courses_id', 'course', 'count']

none_student_id_count = 0

with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/student_course_duplicates/student_course_duplicates.csv'), 'w', encoding='UTF8', newline='') as f:
    
    writer = csv.writer(f)
    writer.writerow(header)
    all_courses = StudentCourse.objects.all()

    list_course_student_id = []

    for course in all_courses:
        list_course_student_id.append(f"{course.course_id}_{course.student_id}")


    duplicates = [f"{item}_{count}" for item, count in collections.Counter(list_course_student_id).items() if count > 1]

    for duplicate in duplicates:
        course_id = duplicate.split("_")[0]
        student_id = duplicate.split("_")[1]
        count = duplicate.split("_")[2]
        if student_id == 'None':
            none_student_id_count += 1
            student_id = None
        student_courses = StudentCourse.objects.filter(course_id=course_id, student_id=student_id).select_related('student', 'course').first()
        for student_course in [student_courses]:
            writer.writerow([
                    student_course.id, 
                    student_course.student_id, 
                    '-' if student_id is None else student_course.student.aadhar_number , 
                    student_course.course_id, 
                    student_course.course.course_name,
                    count ])
    print(none_student_id_count)
    print(len(duplicates))

