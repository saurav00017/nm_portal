from student.models import Student
from datarepo.file_async import sync_file_with_scp

students_list = Student.objects.all().only('provisional_certificate', 'certificate')
total = students_list.count()
for index, student in enumerate(students_list):
    try:
        sync_file_with_scp(student.provisional_certificate)
        sync_file_with_scp(student.certificate)
        print("Pending", total - index)
    except Exception as e:
        print(str(e))
