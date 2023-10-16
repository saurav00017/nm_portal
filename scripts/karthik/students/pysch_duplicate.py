# PsychometricResult
from psychometric.models import PsychometricResult
from django.db.models import Count


a = PsychometricResult.objects.values('student_id').annotate(Count('id')).order_by().where(student__roll_no=621820104006).filter(id__count__gt=1)
b = PsychometricResult.objects.filter(student__roll_no=621820104006)
for bb in b:
    print(bb.client.client.username)