import sys
import csv

filename_a = sys.argv[1]
filename_b = sys.argv[2]

def read(filename):
    with open(filename) as infile:
        reader = csv.DictReader(infile)
        rows = [row for row in reader]

    rows.sort(key=lambda i: i["image"])
    for row in rows:
        row.pop("image")
    return rows

a = read(filename_a)
b = read(filename_b)

for i, j in zip(a, b):
    if i != j:
        print(i)
        print(j)
        print()
    
