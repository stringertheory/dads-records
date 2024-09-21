import sys
import csv
import os
import requests
import collections
import json

from add_to_discogs import username, token, api_url, sleep, batch_field_id

def get_all_releases(folder_id=0, per_page=250, first_page_only=False):
    url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases"
    page = 1
    result = []
    while True:
        response = requests.get(url, params={
            "page": page, "per_page": per_page, "token": token
        })
        sleep(response)
        data = response.json()
        result.extend(data["releases"])
        if data["pagination"]["page"] >= data["pagination"]["pages"] or first_page_only:
            break
        page += 1
    return result

def main():

    session = requests.Session()
    
    releases = get_all_releases()

    for release in releases:

        instance_id = release["instance_id"]
        folder_id = release["folder_id"]
        release_id = release["basic_information"]["id"]

        previous_batch = None
        for note in release["notes"]:
            if note["field_id"] == batch_field_id:
                previous_batch = note["value"]

        if not previous_batch:
            print('could not get previous batch')
            breakpoint()

        new_batch = "".join(reversed([c for c in previous_batch]))

        print(release_id, previous_batch, new_batch)
        url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}/instances/{instance_id}/fields/{batch_field_id}"
        
        print(
            f"adding batch number {new_batch} to {instance_id}",
            file=sys.stderr,
        )
        response = session.post(
            url,
            headers={
                "Content-Type": "application/json",
            },
            params={"token": token},
            data=json.dumps({"value": new_batch}),
        )
        sleep(response)
        

if __name__ == '__main__':
    main()
