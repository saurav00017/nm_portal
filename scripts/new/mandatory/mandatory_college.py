from skillofferings.models import MandatoryCourse, SKillOfferingEnrollment, SKillOffering

college_codes = []
with open('./372.csv', 'r') as file:
    data = file.read()
    college_codes = str(data).strip("\n")

print(len(college_codes))
