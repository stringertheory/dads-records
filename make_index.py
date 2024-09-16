import jinja2
import glob
import csv

def read_pages():
    result = []
    for csv_filename in sorted(glob.glob("records/*/*.csv")):
        batch_number = csv_filename.split('/')[1]
        with open(csv_filename) as infile:
            reader = csv.DictReader(infile)
            rows = [row for row in reader]
        artists = [r['artist'] for r in rows]
        result.append({
            "batch_number": batch_number,
            "artists": artists,
        })
    return result

def main():

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    pages = read_pages()
    print(pages)
    
    html = template_env.get_template("index.html").render(pages=pages)
    html_filename = "records/index.html"
    with open(html_filename, "w") as outfile:
        outfile.write(html)

if __name__ == '__main__':
    main()
