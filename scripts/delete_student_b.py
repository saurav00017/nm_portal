from student.models import Student
from datarepo.models import Branch

repo = [71,122,7029]

for x in repo:
    student_info = Student.objects.filter(rbranch=x)
    print('old count',student_info.count())
    student_info.delete()
    b = Branch.objects.get(id=x).delete()
    
    