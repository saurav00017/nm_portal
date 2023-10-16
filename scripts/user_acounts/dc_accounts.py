from datarepo.models import District
from users.models import User,NMStaffDetails
import csv

file = open('scripts/user_acounts/data.csv')
csv_data = csv.reader(file)
for record in csv_data:
    try:
        district_info = District.objects.get(name=record[0].upper())
        new_user = User.objects.create(
            username = record[1],
            account_role = 12,
        )
        new_user.save()
        new_user.set_password(record[2])
        new_user.save()
        # staff
        new_staff = NMStaffDetails.objects.create(
            user_id = new_user.id,
            district_id = district_info.id
        )
        new_staff.save()
    except District.DoesNotExist:
        print(record[0].upper())