import sys
import base64
import concurrent.futures
import csv
import glob
import json
import os

from openai import OpenAI


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
                            "text": """You are given an image that is a picture of an square album cover on a table. Your task is to identify the coordinates of the corners of the square album cover.

Carefully analyze the image and look for the following elements:
1. The table.
2. The album cover.

Give the x coordinates as fraction of the width of the image. Give the y coordinates as a fraction of the height of the image.

It is possible that an edge or corner of the album cover is cut off in the image. If so, estimate the location of the missing corner or corners, and the coordinate will be a fraction greater than one.

Think step by step before deciding on your final answers.

Use the following format for your response:

{
  "top_left": [x, y],
  "top_right": [x, y],
  "bottom_right": [x, y],
  "bottom_left": [x, y]
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
                    "name": "coord_response",
                    "strict": True,
                    "schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "type": "object",
                        "properties": {
                            "coordinates": {
                                "type": "object",
                                "properties": {
                                    "top_left": {
                                        "type": "object",
                                        "properties": {
                                            "x": {"type": "number"},
                                            "y": {"type": "number"},
                                        },
                                        "required": ["x", "y"],
                                        "additionalProperties": False,
                                    },
                                    "top_right": {
                                        "type": "object",
                                        "properties": {
                                            "x": {"type": "number"},
                                            "y": {"type": "number"},
                                        },
                                        "required": ["x", "y"],
                                        "additionalProperties": False,
                                    },
                                    "bottom_right": {
                                        "type": "object",
                                        "properties": {
                                            "x": {"type": "number"},
                                            "y": {"type": "number"},
                                        },
                                        "required": ["x", "y"],
                                        "additionalProperties": False,
                                    },
                                    "bottom_left": {
                                        "type": "object",
                                        "properties": {
                                            "x": {"type": "number"},
                                            "y": {"type": "number"},
                                        },
                                        "required": ["x", "y"],
                                        "additionalProperties": False,
                                    },
                                },
                                "required": [
                                    "top_left",
                                    "top_right",
                                    "bottom_right",
                                    "bottom_left",
                                ],
                                "additionalProperties": False,
                            }
                        },
                        "required": ["coordinates"],
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
