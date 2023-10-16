import csv
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from college.models import  College
from datarepo.models import Branch
from skillofferings.models import MandatoryCourse, SKillOffering
from django.utils import timezone
import os.path
import os
from django.conf import settings

is_unlimited = False
course_type = 0
now = timezone.now()
update_count = 0
insert_count = 0
null_count = 0
invalid_count = 0
no_action_count = 0 

with open('scripts/mandatory/invalid_rows.csv', 'w', encoding='UTF8', newline='') as invalid_csv_file:
                    writer1 = csv.writer(invalid_csv_file)

with open('scripts/mandatory/null_rows.csv', 'w', encoding='UTF8', newline='') as null_csv_file:
                    writer2 = csv.writer(null_csv_file)

with open(os.path.join(settings.BASE_DIR,'scripts/mandatory/file.csv'), 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  
    for row in reader:
        try:
            college_id= int(row[0])
        except:
            college_id = None
        try:
            skill_offering_id= int(row[1])
        except:
            skill_offering_id = None
        try:
            branch_id = int(row[2])
        except:
            branch_id  = None
        try:
            sem = int(row[3])
        except:
            sem = None
        try:
            count = int(row[4])
        except:
            count = None
        

        if college_id is not None and skill_offering_id is not None and branch_id is not None:
            try:
                college = College.objects.get(id=college_id)
                skill_offering = SKillOffering.objects.get(id=skill_offering_id)
                branch = Branch.objects.get(id=branch_id)

                instance = MandatoryCourse.objects.filter(college_id=college_id,
                                                                       skill_offering_id=skill_offering_id,
                                                                       branch_id=branch_id,
                                                                       sem=sem).first()
                if instance:
                    if instance.count is None or instance.count < count:
                        instance.count = count
                        instance.save()
                        update_count = update_count + 1
                    else:
                        no_action_count = no_action_count + 1
                else:
                    MandatoryCourse.objects.create(college=college,
                                                                 skill_offering=skill_offering,
                                                                 branch=branch,
                                                                 sem=sem,
                                                                 count=count,
                                                                 course_type= course_type,
                                                                 is_unlimited = is_unlimited,
                                                                 created= now,
                                                                 updated = now,
                                                                 )
                    insert_count = insert_count + 1
            except (College.DoesNotExist, SKillOffering.DoesNotExist, Branch.DoesNotExist):
                    writer1.writerow(row)
                    invalid_count = invalid_count + 1
            except IntegrityError:
                    print(f"Integrity error for row: {row}")
        else:
            writer2.writerow(row)
            null_count = null_count + 1


print("Inserted rows:", insert_count)
print("Updated rows:", update_count)
print("N/A or null value rows:", null_count)
print("invalid ids rows:", invalid_count)
print("instance count equal to or greater than csv count:", no_action_count)                