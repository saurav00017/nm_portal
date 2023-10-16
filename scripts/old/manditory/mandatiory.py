import csv
import os
import uuid
import json
from django.conf import settings
import time
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment
from student.models import Student
from django.db.utils import OperationalError

mandatory_courses = SKillOffering.objects.filter(is_mandatory=1)

count = 0
for mandatory_course in mandatory_courses:
    branches = mandatory_course.branch.all()
    for branch in branches:
        temp = []
        eligible_students = None
        try:
            eligible_students = list(Student.objects.filter(branch=branch.name, sem=mandatory_course.sem))
        except:
            time.sleep(1)
            print("reading exception one")
            try:
                eligible_students = list(Student.objects.filter(branch=branch.name, sem=mandatory_course.sem))
            except:
                time.sleep(1)
                print("reading exception one")
                try:
                    eligible_students = list(Student.objects.filter(branch=branch.name, sem=mandatory_course.sem))
                except:
                    time.sleep(1)
                    print("reading exception one")
                    try:
                        eligible_students = list(Student.objects.filter(branch=branch.name, sem=mandatory_course.sem))
                    except:
                        print("failed")
        for eligible_student in eligible_students:
            temp.append(
                SKillOfferingEnrollment(
                    student_id=eligible_student.id,
                    college_id=eligible_student.college.id,
                    knowledge_partner_id=mandatory_course.knowledge_partner.id,
                    skill_offering_id=mandatory_course.id,
                    status=4,
                    offering_type=mandatory_course.offering_type,
                    offering_kind=mandatory_course.offering_kind,
                    is_mandatory=1))
        print(branch.name, mandatory_course.sem, mandatory_course.knowledge_partner.name, mandatory_course.course_name,
              mandatory_course.id, len(temp), sep='||')
        print("executing bulk create")
        try:
            SKillOfferingEnrollment.objects.bulk_create(temp)
            print("bulk complete")
            count = count + 1
        except:
            print(count, "Exception 1")
            try:
                SKillOfferingEnrollment.objects.bulk_create(temp)
                print("bulk complete")
                count = count + 1
            except:
                print(count, "Exception 2")
                try:
                    SKillOfferingEnrollment.objects.bulk_create(temp)
                    print("bulk complete")
                    count = count + 1
                except:
                    print(count, "Exception 3")
                    try:
                        SKillOfferingEnrollment.objects.bulk_create(temp)
                        print("bulk complete")
                        count = count + 1
                    except:
                        print(count, "Exception 4")
                        print("failed")
print("bulk create done")
