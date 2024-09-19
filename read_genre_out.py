import csv
import sys

from selectolax.parser import HTMLParser

# read export
records = {}
with open(sys.argv[1]) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        records[row["release_id"]] = row

with open("genres_out.txt") as infile:
    tree = HTMLParser(infile.read())

total_count = 0
for g in tree.css('genre'):
    print(g.css_first('name').text())
    for i, rid in enumerate(g.css('id'), 1):
        total_count += 1
        r = records[rid.text()]
        print(f"{i}\t{r['Artist']}; {r['Title']} ({r['Released']}, {r['Label']})")
    print()
print()
print("Total", total_count)
# print(tree.css_first('explanations').text())
