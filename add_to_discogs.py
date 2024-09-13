import sys
import csv
import os
import requests
import requests_cache

username = "tomstringer"
folder_id = "7751405" # BeepBopBoop
token = os.getenv("DISCOGS_TOKEN_DAD")
api_url = "https://api.discogs.com"

def main():

    requests_cache.install_cache()
    
    filename = sys.argv[1]
    with open(filename) as infile:
        reader = csv.DictReader(infile)
        data = [row for row in reader if row.get('artist') and row.get('album')]

    for row in data:
        query_params = {
            "q": f"{row['artist']} - {row['album']}",
            "type": "release",
            "token": token,
        }
        print(query_params)

        url = f"{api_url}/database/search"
        response = requests.get(url, params=query_params)
        data = response.json()
        release_id = data["results"][0]["id"]
        breakpoint()

        url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}"
        print(url)

        response = requests.post(url, params={"token": token})
        breakpoint()

if __name__ == '__main__':
    main()
