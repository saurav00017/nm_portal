from college.models import College
from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment
import csv

courses = MandatoryCourse.objects.distinct('skill_offering_id')

header = ['id', 'Course', 'Students Count']

with open('course_allocated_count.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for mc in courses:
        students_assigned_count = SKillOfferingEnrollment.objects.select_related('student', 'skill_offering').filter(
                skill_offering_id=mc.skill_offering_id).count()
        print(students_assigned_count)
        data = [mc.id, mc.skill_offering.course_name, students_assigned_count]
        writer.writerow(data)

