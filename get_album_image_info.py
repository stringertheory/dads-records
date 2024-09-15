import sys
import base64
import concurrent.futures
import csv
import glob
import json
import os
import jinja2

from openai import OpenAI


def get_filenames():
    batch_directory = sys.argv[1]
    if not os.path.isdir(batch_directory):
        raise ValueError(f"{batch_directory} is not a directory")

    batch_number = batch_directory.strip(" /").split("/")[-1]
    
    extension = "*.jpg"
    filename_list = glob.glob(os.path.join(batch_directory, extension))
    print(f"found {len(filename_list)} {extension} files", file=sys.stderr)

    return batch_number, batch_directory, filename_list


def get_image_data(client, image_path):
    with open(image_path, "rb") as image_file:
        print(f"calling gpt-4o with {image_path}", file=sys.stderr)
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are an record collector and music enthusiast with a keen attention to detail.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Your task is to identify the album based on the visual information provided in the image.

Carefully analyze the image and look for the following elements:
1. The name of the artist or band
2. The title of the album
3. The record label of the album
4. The catalog number of the album

First, identify whether these elements are present within the image. Then, identify the album to the best of your ability.

Think step by step before deciding on your final answers.

Use the following format for your response:

{
  "artist": "the name of the artist",
  "album": "the title of the album",
  "record_label": "the record label of the album",
  "catalog_number": "the catalog number of the album",
  "has_record_label": "whether the record label is present within the image",
  "has_catalog_number": "whether the catalog number is present within the image"
}
                            """,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64,"
                                + base64.b64encode(image_file.read()).decode(
                                    "utf-8"
                                ),
                            },
                        },
                    ],
                },
            ],
            max_tokens=300,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "math_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "album": {
                                "type": "string",
                            },
                            "artist": {"type": "string"},
                            "record_label": {"type": "string"},
                            "catalog_number": {"type": "string"},
                            "has_record_label": {"type": "boolean"},
                            "has_catalog_number": {"type": "boolean"},
                        },
                        "required": [
                            "album",
                            "artist",
                            "record_label",
                            "catalog_number",
                            "has_record_label",
                            "has_catalog_number",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
        )

        result = response.choices[0].message.content
        data = json.loads(result)
        data["image"] = image_path
        return data


def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_DAD"))
    
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    
    batch_number, batch_directory, image_filename_list = get_filenames()
    csv_filename = os.path.join(batch_directory, "artist_album.csv")
    html_filename = os.path.join(batch_directory, "index.html")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(get_image_data, client, f): i
            for (i, f) in enumerate(image_filename_list)
        }
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            results.append(future.result())

    results.sort(key=lambda i: i["image"])

    print(f"writing csv with {len(results)} results", file=sys.stderr)
    with open(csv_filename, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "record_label",
                "catalog_number",
                "artist",
                "album",
                "image",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"writing html with {len(results)} results", file=sys.stderr)
    # use relative image path
    for row in results:
        row["img"] = os.path.basename(row["image"])        
    html = template_env.get_template("batch.html").render(
        batch_number=batch_number, results=results,
    )    
    with open(html_filename, "w") as outfile:
        outfile.write(html)


if __name__ == "__main__":
    main()
