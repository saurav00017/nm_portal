from student.models import Student, Branch

students_list = Student.objects.filter(branch__isnull=False, rbranch_id=None).exclude(branch__in='').order_by('branch')

old_branch_name = None
branch_id = None
print("Started")
for student in students_list:
    if old_branch_name != student.branch:
        try:
            get_branch = Branch.objects.get(name__iexact=student.branch)
        except:
            get_branch = Branch.objects.create(name=student.branch)
        old_branch_name = get_branch.name
        branch_id = get_branch.id

    student.rbranch_id = branch_id
    student.save()
print("ENDED")