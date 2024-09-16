import csv
import json
import os
import random
import sys
import time

import requests

username = "tomstringer"
token = os.getenv("DISCOGS_TOKEN_DAD")
api_url = "https://api.discogs.com"
batch_field_id = 4
beep_bop_boop_id = "7751405"
catalog_folder_id = "7758311"
label_folder_id = "7758317"
name_folder_id = "7758320"
manual_folder_id = "7758341"
testing_folder_id = "7758632"

def sleep(response):
    if not hasattr(response, "from_cache") or (hasattr(response, "from_cache") and not response.from_cache):
        delay = 0.6 + random.random()
        print(f"sleep for {delay:.1f}")
        time.sleep(delay)
    else:
        print("cached")


def get_filenames():
    batch_directory = sys.argv[1]
    if not os.path.isdir(batch_directory):
        raise ValueError(f"{batch_directory} is not a directory")

    basename = "artist_album.csv"
    csv_filename = os.path.join(batch_directory, basename)

    batch_number = batch_directory.strip(" /").split("/")[-1]

    msg = f"found {csv_filename}, batch number {batch_number}"
    print(msg, file=sys.stderr)

    return csv_filename, batch_number

def get_best_result(data):
    if data["results"]:
        return data["results"][0]["id"]
            

def main():
    csv_filename, batch_number = get_filenames()

    session = requests.Session()

    with open(csv_filename) as infile:
        reader = csv.DictReader(infile)
        data = [
            row for row in reader if row.get("artist") and row.get("album")
        ]

    for row_number, row in enumerate(data):

        print(f"doing row number {row_number}", file=sys.stderr)

        if row["artist"] in {"Various Artists", "Various", "Unknown"}:
            row["artist"] = ""
        
        queries = []
        if row["catalog_number"] and row["record_label"]:
            queries.append((catalog_folder_id, f"{row['artist']} {row['album']} {row['record_label']} {row['catalog_number']}"))
        if row["record_label"]:
            queries.append((label_folder_id, f"{row['artist']} {row['album']} {row['record_label']}"))
        queries.append((name_folder_id, f"{row['artist']} {row['album']}"))

        # for debugging
        # if row_number > 17: continue
        
        for folder_id, query in queries:
        
            query_params = {
                "q": query,
                "type": "release",
                "token": token,
            }
            
            url = f"{api_url}/database/search"
            print(f"making query {query}", file=sys.stderr)
            response = session.get(url, params=query_params)
            sleep(response)
            data = response.json()
            release_id = get_best_result(data)
            if release_id:
                break

        if not release_id:
            print(f"{'*' * 120}\n\ndidn't find match for {query}\n\n{'*' * 120}", file=sys.stderr)
            continue

        # folder_id = testing_folder_id
        
        url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}"

        print(f"adding release {release_id}", file=sys.stderr)
        response = session.post(url, params={"token": token})
        sleep(response)

        instance_id = response.json()["instance_id"]
        url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}/instances/{instance_id}/fields/{batch_field_id}"

        print(
            f"adding batch number {batch_number} to {instance_id}",
            file=sys.stderr,
        )
        response = session.post(
            url,
            headers={
                "Content-Type": "application/json",
            },
            params={"token": token},
            data=json.dumps({"value": f"{batch_number}"}),
        )
        sleep(response)

        print("", file=sys.stderr)

if __name__ == "__main__":
    main()
