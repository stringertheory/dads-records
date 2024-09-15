import sys
import csv
import os
import requests
import requests_cache
import time

username = "tomstringer"
folder_id = "7751405"  # BeepBopBoop
token = os.getenv("DISCOGS_TOKEN_DAD")
api_url = "https://api.discogs.com"


def sleep(response):
    if hasattr(response, "from_cache") and response.from_cache:
        time.sleep(0.5 + random.random())


def main():
    session = requests_cache.CachedSession(
        "discogs", allowable_methods=("GET", "POST")
    )

    filename = sys.argv[1]
    with open(filename) as infile:
        reader = csv.DictReader(infile)
        data = [
            row for row in reader if row.get("artist") and row.get("album")
        ]

    for row in data:
        query_params = {
            "q": f"{row['artist']} - {row['album']}",
            "type": "release",
            "token": token,
        }

        url = f"{api_url}/database/search"
        response = session.get(url, params=query_params)
        sleep(response)
        data = response.json()
        release_id = data["results"][0]["id"]

        url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}"

        response = session.post(url, params={"token": token})
        sleep(response)


if __name__ == "__main__":
    main()
