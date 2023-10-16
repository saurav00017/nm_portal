with open('student_ids.csv', 'r') as file1:
    data = file1.read()

    student_1 = str(data).split(",")
    print(len(student_1))
with open('student_ids1.csv', 'r') as file2:
    data = file2.read()

    student_2 = str(data).split(",")
    print(len(student_2))

not_present = []

for id in student_1:
    if id not in student_2:
        not_present.append(id)

print(not_present)
print(len(not_present))