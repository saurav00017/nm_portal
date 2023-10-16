import csv
import os
from django.conf import settings
from users.models import User, UserDetail
from django.db.models import Count
from itertools import groupby

def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

header = ['username', 'user_id', 'count']

users = UserDetail.objects.all().values('user_id', "user__username").annotate(total=Count('user_id')).filter(user__account_role=8).filter(total__gt=1)

with open(os.path.join(settings.BASE_DIR, 'scripts/karthik/users/duplicate.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    print(len(users))
    for user in users:
        ud = UserDetail.objects.filter(user_id=user["user_id"])
        # print(user["user__username"])
        writer.writerow([
            user["user__username"],
            user["user_id"],
            user["total"]
        ]) 
        writer.writerow([])
        list_ids = []
        for u in ud:
            list_ids.append(u.student_id)
        if all_equal(list_ids):
            print(all_equal(list_ids), user["user__username"])
        for u in ud:
            # if u.student_id is None:
            #     u.delete()
            writer.writerow([
                user["user__username"],
                user["user_id"],
                u.student_id if u.student_id else None,
            ]) 
        writer.writerow([])
        writer.writerow([])
        