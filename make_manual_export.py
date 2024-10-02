import csv

from reverse_batch_names import get_all_releases


def main():
    releases = get_all_releases(per_page=250, first_page_only=False)

    with open("genre_export.csv", "w") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["release_id", "genres", "styles", "title", "artists"],
        )
        writer.writeheader()
        for release in releases:
            info = release["basic_information"]
            release_id = info["id"]
            row = {
                "release_id": release_id,
                "title": info["title"],
                "artists": ", ".join(a["name"] for a in info["artists"]),
                "genres": ", ".join(info["genres"]),
                "styles": ", ".join(info["styles"]),
            }
            writer.writerow(row)


if __name__ == "__main__":
    main()
