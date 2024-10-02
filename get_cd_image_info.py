import sys
import base64
import concurrent.futures
import csv
import glob
import json
import os

from openai import OpenAI

{
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "loc": {
                "type": "string"
            },
            "toll": {
                "type": ["string", "null"]
            },
            "message": {
                "type": ["string", "null"]
            }
        },
        "required": [
            "loc"
        ]
    }
}

def get_image_data(client, image_path):
    with open(image_path, "rb") as image_file:
        print(f"calling gpt-4o with {image_path}", file=sys.stderr)
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are an music collector and music enthusiast with a keen attention to detail.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Your task is to identify a group of twelve CDs based on the visual information provided in the image.

Carefully analyze the image and look for the following elements:
1. The name of the artists or bands
2. The titles of the album
3. The record label of the albums
4. The catalog number of the albums

First, identify whether these elements are present within the image of each CD. Then, identify the album to the best of your ability.

Think step by step before deciding on your final answers.

Use the following format for your each CD in your response:

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
            max_tokens=300*12,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "cd_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "albums": {
                                "type": "array",
                                "items": {
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
                            }
                        },
                        "required": ["albums"],
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

    image_filename = sys.argv[1]
    result = get_image_data(client, image_filename)

    breakpoint()

if __name__ == "__main__":
    main()
