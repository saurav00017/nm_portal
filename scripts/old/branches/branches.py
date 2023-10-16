import csv

file = open('/Users/vjpranay/Projects/nm_portal/nm_portal/scripts/branches/b.csv')
csv_data = csv.reader(file)
counter = 0
branches = []
for record in csv_data:
    branches.append(record[0])
print(branches)