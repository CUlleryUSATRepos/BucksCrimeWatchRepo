import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

URL = "https://crimewatch.net/us/pa/bucks/directory"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def main():
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    agencies = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        name = a.get_text(strip=True)

        if not name:
            continue

        if re.search(r"/\d{5}$", href) or "sheriff" in href.lower():
            agencies.append({
                "agency_name": name,
                "agency_url": href
            })

    df = pd.DataFrame(agencies).drop_duplicates()

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/agency_links.csv", index=False)

    print(df)


if __name__ == "__main__":
    main()