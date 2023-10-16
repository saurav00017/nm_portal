from college.models import College
from datarepo.models import District

combo_district_ids = [
    [49, 19],
    [51, 9],
    [40, 7],
    [39, 26]
]

for district_ids in combo_district_ids:
    district_list = District.objects.filter(id__in=district_ids)
    first_district = district_list.first()

    colleges_list = College.objects.filter(district_id__in=district_ids).update(
        district_id=first_district.id
    )
    for remain_dist in district_list.exclude(id=first_district.id):
        print(remain_dist.id, remain_dist.name)
        remain_dist.delete()

