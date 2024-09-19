import sys
import csv

with open(sys.argv[1]) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        print("<record><id>{release_id}</id><artist>{Artist}</artist><title>{Title}</title><label>{Label}</label><release_year>{Released}</release_year></record>".format(**row))
