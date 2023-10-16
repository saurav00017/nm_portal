from django.db.models import Count
from skillofferings.models import FeedBack, SKillOfferingEnrollment, SKillOffering
import os
from django.conf import settings


feedbacks = FeedBack.objects.values(
    'course_name',
).annotate(count=Count('course_name')).order_by()

for feedback in feedbacks:
    print(f"{feedback['course_name']} \t {feedback['count']}")
