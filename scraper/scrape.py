import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import sqlite3
from helpers import fetch_html_with_cookie

DB_PATH = "cars.db"


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


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    sql = """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            mileage TEXT,
            url TEXT,
            year TEXT,
            place TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(price, mileage, url)
        )
    """
    c.execute(sql)
    conn.commit()
    conn.close()


def insert_new_cars(cars: List[Dict[str, Any]]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_count = 0
    for car in cars:
        try:
            c.execute(
                """
                INSERT INTO cars (title, price, mileage, url, year, place)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    car["title"],
                    car["price"],
                    car["mileage"],
                    car["url"],
                    car["year"],
                    car["place"],
                ),
            )
            new_count += 1
        except sqlite3.IntegrityError:
            continue
    conn.commit()
    conn.close()
    print(f"Inserted {new_count} new cars into the database.")


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
    init_db()
    insert_new_cars(raw_cars)
