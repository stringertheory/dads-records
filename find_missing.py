import sys
import csv
import collections

grouped = collections.defaultdict(list)
with open(sys.argv[1]) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        grouped[int(row["Collection Batch"])].append(row)

for batch, row_list in sorted(grouped.items()):
    print(batch, len(row_list))
    # if batch == 107:
    #     for row in sorted(row_list, key=lambda i: i["Artist"]):
    #         print(row["Artist"], row["Title"])

batch = 107
with open("col", "w") as outfile:
    for row in sorted(grouped[107], key=lambda i: (i["Artist"].lower(), i["Title"].lower())):
        print(row["Artist"], row["Title"], file=outfile)

with open(f"records/{batch}/artist_album.csv") as infile, open("fol", "w") as outfile:
    reader = csv.DictReader(infile)
    for row in sorted(reader, key=lambda i: (i['artist'].lower(), i['album'].lower())):
        print(row['artist'], row['album'], file=outfile)


    
