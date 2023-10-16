
from student.models import Student
# from django.db.models import Max, Count

# dup_students = Student.objects.values('aadhar_number','roll_no') \
#     .annotate(records=Count('aadhar_number')) \
#     .filter(records__gt=1)

# print(dup_students.count())
    
all = Student.objects.all()
print('id','roll','college','college_type','college_name','name','email','phone','branch_id','branch','sem','verification','registration',sep=',')
for x in all:
    print(x.id,x.roll_no,x.college_id,x.college.college_type if x.college else None,x.college.college_name if x.college else None,x.aadhar_number,x.email,x.phone_number,x.rbranch_id,x.rbranch.name if x.rbranch else None ,x.sem,x.verification_status,x.registration_status,sep=',')