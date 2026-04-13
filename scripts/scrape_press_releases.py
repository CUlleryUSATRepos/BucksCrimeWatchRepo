import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

AGENCY_FILE = "data/agency_links.csv"
OUTPUT_FILE = "data/today_posts.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrape_agency(agency_url):
    response = requests.get(agency_url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    posts = []

    cards = soup.find_all("div", class_="news-single-card")

    for card in cards:
        title_tag = card.select_one("h3 a")
        date_tag = card.select_one("div.single-news-date")
        summary_tag = card.select_one("div.single-news-subtitle")

        if not title_tag or not date_tag:
            continue

        title = title_tag.get_text(" ", strip=True)
        link = urljoin(agency_url, title_tag.get("href", "").strip())
        date_text = date_tag.get_text(" ", strip=True)
        summary = summary_tag.get_text(" ", strip=True) if summary_tag else ""

        posts.append({
            "title": title,
            "date": date_text,
            "summary": summary,
            "link": link
        })

    df = pd.DataFrame(posts).drop_duplicates(subset=["title", "link"])
    return df


def main():
    agencies = pd.read_csv(AGENCY_FILE)
    all_dfs = []

    for _, row in agencies.iterrows():
        agency_name = row["agency_name"]
        agency_url = row["agency_url"]

        print(f"Scraping: {agency_name}")

        try:
            df = scrape_agency(agency_url)

            if not df.empty:
                df["agency_name"] = agency_name
                df["agency_page"] = agency_url
                all_dfs.append(df)

        except Exception as e:
            print(f"FAILED: {agency_name} -> {e}")

        time.sleep(1)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=[
            "title", "date", "summary", "link", "agency_name", "agency_page"
        ])

    # "Created Mar 20, 2026" -> datetime
    final_df["date_clean"] = (
        final_df["date"]
        .astype(str)
        .str.replace("Created ", "", regex=False)
        .str.replace("Updated ", "", regex=False)
        .str.strip()
    )

    final_df["date_parsed"] = pd.to_datetime(final_df["date_clean"], errors="coerce")
    today = datetime.now().date()

    final_df = final_df[
        final_df["date_parsed"].notna() &
        (final_df["date_parsed"].dt.date == today)
    ].copy()

    final_df = final_df.drop(columns=["date_clean", "date_parsed"])
    final_df = final_df.drop_duplicates(subset=["title", "link", "agency_name"])

    print(final_df)
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(final_df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()