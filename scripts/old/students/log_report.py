from student.models import Student


def complete_report(last_batch_level_count: int = 0):
    students = Student.objects.exclude(college_id__isnull=True)
    print(f"Total Students ---------------------------------------------{students.count()}")
    print(f"Total Students ---------------------------------------------{students.count()}")

