import sys
import csv
import os
import requests
import requests_cache
import collections

from add_to_discogs import username, folder_id, token, api_url

def get_all_releases():
    url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases"
    page = 1
    result = []
    while True:
        response = requests.get(url, params={
            "page": page, "per_page": 100, "token": token
        })
        data = response.json()
        result.extend(data["releases"])
        if data["pagination"]["page"] >= data["pagination"]["pages"]:
            break
        page += 1
    return result

def main():
    releases = get_all_releases()

    grouped = collections.defaultdict(list)
    for release in releases:
        grouped[release["id"]].append(release["instance_id"])

    for release_id, instance_id_list in grouped.items():
        if len(instance_id_list) > 1:
            for instance_id in instance_id_list[1:]:
                print('deleting', release_id, instance_id)
                url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}/instances/{instance_id}"
                requests.delete(url, params={"token": token})


if __name__ == '__main__':
    main()
