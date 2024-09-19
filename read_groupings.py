import csv
import sys

from selectolax.parser import HTMLParser

# read export
records = {}
with open(sys.argv[1]) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        records[row["release_id"]] = row

with open("groupings.txt") as infile:
    tree = HTMLParser(infile.read())

total_count = 0
groupings = tree.css_first('groupings')
for group in groupings.css('group'):
    print('-' * 10 + group.css_first("theme").text() + "-" * 10)
    print(group.css_first("explanation").text())
    print()
    for i, release_id in enumerate(group.css("id"), 1):
        total_count += 1
        r = records[release_id.text()]
        print(f"{i}\t{r['Artist']}; {r['Title']} ({r['Released']}, {r['Label']})")
    print()

print("-" * 10 + "UNGROUPED" + "-" * 10)
ungrouped = groupings.css_first('ungrouped')
if ungrouped:
    for i, release_id in enumerate(ungrouped.css("id"), 1):
        cg = release_id.next.text()
        r = records[release_id.text()]
        r = records[release_id.text()]
        print(f"{i}\tmaybe {cg}\t{r['Artist']}; {r['Title']} ({r['Released']}, {r['Label']})")

print()
print("Total", total_count)
# print(tree.css_first('explanations').text())
