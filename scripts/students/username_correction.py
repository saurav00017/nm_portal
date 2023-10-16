from users.models import UserDetail, User
from datarepo.models import CollegeType
from college.models import College
import csv
import os
from django.conf import settings
colleges_list = College.objects.filter(college_type=CollegeType.ARTS_AND_SCIENCE)

headers = ['college_id', 'college_code', 'college_name', 'student_id', 'student_roll_no', 'old_username', 'new_username', "error"]

with open(os.path.join(settings.BASE_DIR, "scripts/students/as_students_username_update.csv"), 'w') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    total_count = colleges_list.count()
    index = 0
    for college in colleges_list:
        print("Pending --> ", total_count - index)
        index += 1
        college_code = college.college_code
        college_code = str(college_code).replace(" ","")
        user_details = UserDetail.objects.filter(
            user__username__istartswith=f"as{college_code}{college_code}",
            student__college_id=college.id)

        college_id = college.id
        college_name = college.college_name
        for _user in user_details:
            record = [
                college_id,
                college_code,
                college_name,
                _user.student_id,
                _user.student.roll_no,
                _user.user.username,
            ]
            try:
                old_username = _user.user.username
                new_username = str(old_username).split(college_code, 1)[1]

                print(new_username)
                try:
                    user = User.objects.get(username=new_username).exclude(id=_user.user_id)
                    record += [None, "New Username already exists to another user"]
                except:
                    _user.user.username = new_username
                    _user.user.save()
                    record += [new_username]
            except Exception as e:
                record += [None, str(e)]

            writer.writerow(record)
