import sys
import csv
import requests
import os

from add_to_discogs import api_url, sleep

def read_spreadsheet(filename):
    with open(filename) as infile:
        reader = csv.DictReader(infile)
        return [row for row in reader]


def main():

    # 1131 left
    
    session = requests.Session()
    
    username = 'mstring'
    token = os.getenv("DISCOGS_TOKEN_MIKE")
    folder_id = 0
    filename = sys.argv[1]
    rows = read_spreadsheet(filename)
    for i, row in enumerate(rows):
        release_id = row["release_id"]

        if row["Collection Family"] != "mike":
            continue
    
        url = f"{api_url}/users/{username}/collection/folders/{folder_id}/releases/{release_id}"
        print(f"{i}: adding release {release_id}", file=sys.stderr)
        response = session.post(url, params={"token": token})
        sleep(response)
        print(response.status_code, file=sys.stderr)
        print("", file=sys.stderr)

        
if __name__ == '__main__':
    main()
