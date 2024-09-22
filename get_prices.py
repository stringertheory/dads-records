import datetime
import json
import re
import time

import requests
import requests_cache
from selectolax.parser import HTMLParser

from reverse_batch_names import get_all_releases, sleep


def fetch_page(session, release_id, page=1):
    url = f"https://www.discogs.com/sell/release/{release_id}"
    params = {"sort": "price,desc", "limit": 250, "ev": "rb"}
    if page > 1:
        params["page"] = page
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    }
    response = session.get(
        url,
        params=params,
        headers=headers,
    )
    sleep(response)
    return response


def parse_statistics_section(tree):
    statistics = {}

    # Find the div with id="statistics"
    statistics_section = tree.css_first("div.statistics")

    # Loop through each <li> and extract key-value pairs
    for item in statistics_section.css("li"):
        key = item.text().split(":")[0].strip(": \n").strip()
        value = item.text().split(":")[1].strip(": \n").strip()
        statistics[key] = value

    return statistics


def parse_records_for_sale(tree, conversions):
    records = []

    # Locate the table with the records using the <tr> elements
    for tr in tree.css("tr.shortcut_navigable"):
        record = {}

        # condition
        notes = tr.css_first("p.item_condition + p.hide_mobile").text().strip()

        media_condition = None
        sleeve_condition = None
        keys = tr.css("span.condition-label-mobile")
        values = tr.css("span.condition-label-mobile + span")
        for k, v in zip(keys, values):
            if k.text().strip() == "Media:":
                media_condition = v.text().strip().split("\n")[0].strip()
            if k.text().strip() == "Sleeve:":
                sleeve_condition = v.text().strip().split("\n")[0].strip()

        # seller info
        seller_name = tr.css_first("div.seller_block a").text().strip()
        try:
            seller_ratings = (
                tr.css_first("span.star_rating").parent.text().strip()
            )
        except AttributeError:
            seller_ratings = "New Seller"
        ships_from = None
        for span in tr.css("td.seller_info span.mplabel"):
            if span.text().strip().lower() == "ships from:":
                ships_from = span.parent.text().split(":")[-1].strip()

        # price info
        price_el = tr.css_first("span.price")
        price_currency = price_el.attrs.get("data-currency")
        price_value = price_el.attrs.get("data-pricevalue")
        conversion_rate = conversions[price_currency]
        price_dollars = round(float(price_value) / float(conversion_rate), 2)
        shipping = (
            tr.css_first("span.item_shipping")
            .text()
            .strip()
            .split("\n")[0]
            .strip()
        )

        shipping_value = "".join(
            [i for i in shipping if i.isdigit() or i == "."]
        )
        try:
            total_price = tr.css_first("span.converted_price").text.strip()
        except AttributeError:
            total_price = str(price_value)
        total_price_dollars = float(
            "".join([i for i in total_price if i.isdigit() or i == "."])
        )

        # make record
        record["media_condition"] = media_condition
        record["sleeve_condition"] = sleeve_condition
        record["seller_info"] = {
            "seller_name": seller_name,
            "seller_ratings": seller_ratings,
            "ships_from": ships_from,
        }
        record["price_info"] = {
            "price": price_value,
            "shipping": shipping_value,
            "currency": price_currency,
            "price_dollars": price_dollars,
            "total_price_dollars": total_price_dollars,
        }
        record["notes"] = notes

        # Append the record to the list
        records.append(record)

    return records


def get_currency_conversions():
    response = requests.get(
        "https://cdn.jsdelivr.net/gh/prebid/currency-file@1/latest.json"
    )
    return response.json()["conversions"]["USD"]


def parse_page(response, conversions):
    tree = HTMLParser(response.content)

    total = (
        tree.css_first("strong.pagination_total")
        .text()
        .strip()
        .split()[-1]
        .strip()
    )
    next_page = tree.css_first("a.pagination_next")
    if next_page:
        next_page = int(next_page.attrs["href"].rsplit("=", 1)[-1])

    # Parse the statistics section
    statistics = parse_statistics_section(tree)

    # Parse the records for sale section
    records_for_sale = parse_records_for_sale(tree, conversions)

    # Combine the parsed data into a structured dictionary
    parsed_data = {
        "response_date": response.headers["Date"],
        "run_timestamp": int(time.time()),
        "n_for_sale": total,
        "statistics": statistics,
        "records_for_sale": records_for_sale,
    }

    # Convert the dictionary to a JSON string and return
    return parsed_data, next_page


def main():
    session = requests_cache.CachedSession("cache/prices")

    conversions = get_currency_conversions()

    releases = get_all_releases(per_page=250, first_page_only=False)

    for release in releases:
        release_id = release["basic_information"]["id"]
        print(release_id)
        response = fetch_page(session, release_id, page=1)
        parsed_json, next_page = parse_page(response, conversions)
        while next_page:
            response = fetch_page(session, release_id, page=next_page)
            next_json, next_page = parse_page(response, conversions)
            parsed_json["records_for_sale"].extend(
                next_json["records_for_sale"]
            )

        parsed_json["release_id"] = release_id
        print(parsed_json["n_for_sale"])
        print()
        with open(f"prices.jsonl", "a") as outfile:
            outfile.write(json.dumps(parsed_json))
            outfile.write("\n")
            outfile.flush()


if __name__ == "__main__":
    main()
