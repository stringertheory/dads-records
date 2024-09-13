import base64
import concurrent.futures
import csv
import glob
import json

from openai import OpenAI

client = OpenAI()


def get_image_data(image_path):
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


results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {
        executor.submit(get_image_data, f): i
        for (i, f) in enumerate(glob.glob("vinyls/*.jpg"))
    }
    for future in concurrent.futures.as_completed(futures):
        i = futures[future]
        results.append(future.result())

with open("results.csv", "w") as csvfile:
    print("results", results)
    writer = csv.DictWriter(
        csvfile, fieldnames=["artist", "album", "is_record", "image"]
    )
    writer.writeheader()
    writer.writerows(results)
