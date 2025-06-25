import json
from typing import List, Dict, Any
import sqlite3

from helpers import (
    extract_model_name,
    extract_plate_from_url,
    normalize_plate_number,
    get_apk_expiry_from_rdw,
)

from finnik import (
    get_Finnik_page,
    get_version_name_from_finnik,
)
from anwb import get_rijklaarprijs
from llm import get_llm_summary
from scrape import DB_PATH


def normalize_car_data(raw_car: Dict[str, Any], cookies: dict) -> Dict[str, Any]:
    price_str = raw_car["price"]
    price_num = int("".join(filter(str.isdigit, price_str))) if price_str else 0
    mileage_str = raw_car["mileage"]
    mileage_num = int("".join(filter(str.isdigit, mileage_str))) if mileage_str else 0
    url = raw_car["url"]
    plate = extract_plate_from_url(url, cookies)
    normalize_plate = normalize_plate_number(plate)
    finnik_url = get_Finnik_page(normalize_plate)
    original_name = extract_model_name(raw_car["title"])
    name = get_version_name_from_finnik(original_name, normalize_plate)
    estimated_price = get_rijklaarprijs(mileage_num, plate, name)
    return {
        "url": url,
        "name": name,
        "price_num": price_num,
        "mileage_num": mileage_num,
        "plate": plate,
        "apk_expiry": get_apk_expiry_from_rdw(normalize_plate),
        "finnik_url": finnik_url,
        "estimated_price": estimated_price,
    }


def create_normalized_table(conn):
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS normalized_cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            name TEXT,
            price_num INTEGER,
            mileage_num INTEGER,
            plate TEXT,
            apk_expiry TIMESTAMP,
            finnik_url TEXT,
            estimated_price INTEGER,
            llm_summary TEXT,
            llm_score INTEGER
        )
        """
    )
    conn.commit()


def fetch_new_raw_cars(conn) -> list:
    c = conn.cursor()
    c.execute(
        """
        SELECT title, price, mileage, url, year, place, scraped_at
        FROM raw_cars
        WHERE DATE(scraped_at) = DATE('now', 'localtime')
        """
    )
    rows = c.fetchall()
    return [
        {
            "title": row[0],
            "price": row[1],
            "mileage": row[2],
            "url": row[3],
            "year": row[4],
            "place": row[5],
            "scraped_at": row[6],
        }
        for row in rows
    ]


def is_already_normalized(conn, raw_car: Dict[str, Any]) -> bool:
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM normalized_cars WHERE url = ?",
        (raw_car["url"],),
    )
    return c.fetchone() is not None


def insert_normalized_car(
    conn,
    norm_car: Dict[str, Any],
    llm_summary: str,
    llm_score: int,
):
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO normalized_cars
        (url, name, price_num, mileage_num, plate, apk_expiry, finnik_url, estimated_price, llm_summary, llm_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            norm_car["url"],
            norm_car["name"],
            norm_car["price_num"],
            norm_car["mileage_num"],
            norm_car["plate"],
            norm_car["apk_expiry"],
            norm_car["finnik_url"],
            norm_car["estimated_price"],
            llm_summary,
            llm_score,
        ),
    )
    conn.commit()


def normalize_and_save(cookies: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    create_normalized_table(conn)
    raw_cars = fetch_new_raw_cars(conn)
    new_count = 0
    for raw_car in raw_cars:
        if is_already_normalized(conn, raw_car):
            continue
        norm_car = normalize_car_data(raw_car, cookies)
        llm_summary, llm_score = get_llm_summary(norm_car)
        insert_normalized_car(conn, norm_car, llm_summary, llm_score)
        new_count += 1
    conn.close()
    print(f"Inserted {new_count} new normalized cars into the database.")
