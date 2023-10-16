import csv
import os
import uuid
from django.conf import settings
import json
from college.models import College
from student.models import Student
from datarepo.models import Branch
from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from skillofferings.models import SKillOfferingEnrollment, SKillOffering, MandatoryCourse


mandatory_courses = SKillOffering.objects.filter(
    is_mandatory = 1
)

for x in mandatory_courses:
    e = SKillOfferingEnrollment.objects.filter(skill_offering_id=x.id,is_mandatory=1)
    print(e.count())