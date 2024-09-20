import csv
import glob
import os
import sys

import jinja2


def main():
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    batches = []
    for path in sorted(glob.glob("records/*")):
        if os.path.isdir(path):
            batch_number = os.path.basename(path)
            batches.append(
                {
                    "number": batch_number,
                    "link": f"/records/{batch_number}/",
                }
            )

    for batch in batches:
        batch_number = batch["number"]
        csv_filename = f"records/{batch_number}/artist_album.csv"
        html_filename = f"records/{batch_number}/index.html"
        with open(csv_filename) as csvfile:
            reader = csv.DictReader(csvfile)
            results = [row for row in reader]

        print(f"writing html with {len(results)} results", file=sys.stderr)
        # use relative image path
        for row in results:
            row["img"] = os.path.basename(row["image"])
        html = template_env.get_template("batch.html").render(
            batch_number=batch_number,
            results=results,
            batches=batches,
        )
        with open(html_filename, "w") as outfile:
            outfile.write(html)


if __name__ == "__main__":
    main()
