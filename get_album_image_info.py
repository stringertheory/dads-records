import sys
import base64
import concurrent.futures
import csv
import glob
import json
import os

from openai import OpenAI


def get_filenames():
    batch_directory = sys.argv[1]
    if not os.path.isdir(batch_directory):
        raise ValueError(f"{batch_directory} is not a directory")

    extension = "*.jpg"
    filename_list = glob.glob(os.path.join(batch_directory, extension))
    print(f"found {len(filename_list)} {extension} files", file=sys.stderr)

    out_filename = os.path.join(batch_directory, "artist_album.csv")
    return out_filename, filename_list


def get_image_data(client, image_path):
    with open(image_path, "rb") as image_file:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are an record collector and music enthusiast with an encyclopedic knowledge of all kinds of music.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """What album is in this image?

                            Return a json with:
                            - is_record: true of false, whether there is an album in the image
                            - artist: The name of the artist.
                            - album: The name of the album.

                            Make your best guesses even if you are not sure.
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
                            "is_record": {"type": "boolean"},
                        },
                        "required": ["album", "artist", "is_record"],
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

    out_filename, image_filename_list = get_filenames()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(get_image_data, client, f): i
            for (i, f) in enumerate(image_filename_list)
        }
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            results.append(future.result())

    print(f"writing {len(results)} results", file=sys.stderr)
    with open(out_filename, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["artist", "album", "is_record", "image"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
