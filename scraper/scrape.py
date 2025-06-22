import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from helpers import fetch_html_with_cookie

RAW_JSON = "raw_cars.json"


def extract_raw_data_from_html(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        print("No __NEXT_DATA__ script found")
        return []

    data = json.loads(script.string)
    occasions = (
        data.get("props", {})
        .get("pageProps", {})
        .get("initialState", {})
        .get("searchReducer", {})
        .get("occasions", [])
    )
    return occasions


def scrape_and_save_raw(url: str, cookies: dict) -> None:
    html = fetch_html_with_cookie(url, cookies)
    occations = extract_raw_data_from_html(html)
    raw_cars = []
    for occ in occations:
        other_portal = next(
            (p for p in occ.get("portals", []) if p.get("type") == "other"), None
        )
        title = occ.get("title")
        url = other_portal["url"] if other_portal else None
        raw_cars.append(
            {
                "title": title,
                "price": occ.get("price"),
                "mileage": occ.get("km"),
                "url": url,
                "year": occ.get("year"),
                "place": occ.get("place"),
            }
        )
    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_cars, f, ensure_ascii=False, indent=2)
    print(f"Scraped {len(raw_cars)} raw cars. Saved to {RAW_JSON}.")
