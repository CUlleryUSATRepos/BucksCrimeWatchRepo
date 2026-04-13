import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

AGENCY_CSV = "data/agency_links.csv"
OUTPUT_CSV = "data/all_press_releases.csv"


def load_agencies():
    df = pd.read_csv(AGENCY_CSV)

    required_cols = {"agency_name", "agency_url"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"agency_links.csv is missing columns: {missing}")

    df = df.dropna(subset=["agency_url"]).copy()
    df["agency_name"] = df["agency_name"].astype(str).str.strip()
    df["agency_url"] = df["agency_url"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["agency_url"])

    return df


def scrape_agency_press_releases(agency_name, agency_url):
    response = requests.get(agency_url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    records = []

    for article in soup.find_all("article"):
        title_tag = article.find(["h2", "h3"])
        link_tag = article.find("a", href=True)
        time_tag = article.find("time")

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(" ", strip=True)
        link = urljoin(agency_url, link_tag["href"])
        published_date = time_tag.get_text(" ", strip=True) if time_tag else ""

        records.append({
            "agency_name": agency_name,
            "agency_url": agency_url,
            "title": title,
            "published_date": published_date,
            "release_url": link
        })

    return records


def main():
    agencies = load_agencies()
    all_records = []

    for i, row in agencies.iterrows():
        agency_name = row["agency_name"]
        agency_url = row["agency_url"]

        print(f"Scraping: {agency_name} | {agency_url}")

        try:
            records = scrape_agency_press_releases(agency_name, agency_url)
            print(f"  Found {len(records)} records")
            all_records.extend(records)
        except Exception as e:
            print(f"  FAILED: {e}")

        time.sleep(1)

    results = pd.DataFrame(all_records)

    if not results.empty:
        results = results.drop_duplicates(subset=["agency_name", "title", "release_url"])

    os.makedirs("data", exist_ok=True)
    results.to_csv(OUTPUT_CSV, index=False)

    print(f"\nSaved {len(results)} total records to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()