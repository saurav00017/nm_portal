from kp.models import KnowledgePartner
from simple.models import SimpleCourse
from django.conf import settings
import os
import csv

file = open(os.path.join(settings.BASE_DIR, 'scripts/courses/new1.csv'), 'r')
csv_data = csv.reader(file)
counter = 0
for record in csv_data:
    category = record[1]
    name = record[2]
    course_type = record[4]
    link = record[5]
    partner = record[6]
    hours = record[7]
    try:
        new_kp = KnowledgePartner.objects.get(
            name=partner,
        )
    except KnowledgePartner.DoesNotExist:
        new_kp = KnowledgePartner.objects.create(
            name=partner,
        )
        new_kp.save()
    new_course = SimpleCourse.objects.create(
        name=name,
        category=category,
        course_type=course_type,
        link=link,
        hours=hours,
        knowledge_partner_id=new_kp.id,
    )
