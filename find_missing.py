import sys
import csv
import collections
import glob

grouped = collections.defaultdict(list)
with open(sys.argv[1]) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        # print(row)
        grouped[int(row["Collection Batch"])].append(row)

diff_batches = []
for batch, row_list in sorted(grouped.items()):
    with open(f"records/{batch}/artist_album.csv") as infile:
        reader = csv.DictReader(infile)
        rows = [row for row in reader]
    pix = glob.glob(f"records/{batch}/*.jpg")
    print(batch, len(row_list), len(rows), len(pix))
    if len(row_list) != len(rows):
        diff_batches.append(batch)
        print("nope", batch, len(row_list), "!=", len(rows))
    # assert len(row_list) == len(rows) == len(pix)
    # if batch == 107:
    #     for row in sorted(row_list, key=lambda i: i["Artist"]):
    #         print(row["Artist"], row["Title"])

for batch in diff_batches:
    with open(f"{batch}-collection.csv", "w") as outfile:
        for row in sorted(grouped[batch], key=lambda i: (i["Artist"].lower(), i["Title"].lower())):
            print(row["Artist"], row["Title"], file=outfile)

    with open(f"records/{batch}/artist_album.csv") as infile, open(f"{batch}-folder.csv", "w") as outfile:
        reader = csv.DictReader(infile)
        for row in sorted(reader, key=lambda i: (i['artist'].lower(), i['album'].lower())):
            print(row['artist'], row['album'], file=outfile)


    
