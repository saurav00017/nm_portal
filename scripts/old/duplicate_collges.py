from django.db.models import Count
from college.models import College

duplicates = College.objects.values(
    'college_code'
    ).annotate(name_count=Count('college_code')).filter(name_count__gt=1)

print(duplicates)


