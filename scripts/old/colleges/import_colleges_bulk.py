import csv
import os
from college.models import College
import uuid
import json
from datarepo.models import District
from django.conf import settings


def get_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1]


def get_password_uid():
    return str(uuid.uuid4()).replace("-", "")[::-1][:8]


success_data = []
failed_data = []
file = open(os.path.join(settings.BASE_DIR, 'scripts/colleges/engineering.csv'))
csv_data = csv.reader(file)
counter = 0
for record in csv_data:
    # "0 -INSCODE","1 - INSNAME"," 2- ADDRESS","3 - PINCODE","4 - DISTRICT","5 - TALUK"
    # 0 102,INSTITUTE OF PRINTING TECHNOLOGY,600113,CHENNAI,SAIDAPET,"THARAMANI, CHENNAI"
    try:

        college_code = record[0]
        college_name = record[1]
        pincode = record[2]
        district = record[3]
        taluk = record[4]
        address = record[5]
        district_id = None

        if district:
            district = str(district).strip()

            try:
                get_district = District.objects.get(name__iexact=district)
                district_id = get_district.id
            except:
                new_disct = District.objects.create(
                    name=district
                )
                district_id = new_disct.id

        print(college_name)
        """
        :college_type
        ARTS_AND_SCIENCE = 1
        ENGINEERING = 2
        ITI = 3
        POLYTECHNIC = 4
        PHARMA = 5
        """
        new_college = College.objects.create(
            invitation_id=get_uid(),
            status=0,
            college_name=college_name,
            college_code=college_code,
            address=address,
            pincode=int(pincode) if pincode else None,
            taluk=taluk,
            district_id=district_id,
            college_type=2
        )

        success_data.append({
            "college_name": college_name,
            "college_id": new_college.id,
        })
    except Exception as e:
        print(e)

        failed_data.append({
            "college_name": college_name,
        })
context = {
    "success": success_data,
    "failed": failed_data,
}
print(json.dumps(context))
