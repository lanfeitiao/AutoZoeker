import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import sqlite3
from helpers import fetch_html_with_cookie
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "cars.db"


def extract_raw_data_from_html(html: str) -> List[Dict[str, Any]]:
    try:
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script or not script.string:
            logger.warning("No __NEXT_DATA__ script found or script is empty")
            return []

        data = json.loads(script.string)
        occasions = (
            data.get("props", {})
            .get("pageProps", {})
            .get("initialState", {})
            .get("searchReducer", {})
            .get("occasions", [])
        )

        if not occasions:
            logger.warning("No occasions found in the data")

        return occasions

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from script tag: {e}")
        return []
    except Exception as e:
        logger.error(f"Error extracting data from HTML: {e}")
        return []


def init_db() -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            # Fixed: Removed trailing comma in SQL
            sql = """
                CREATE TABLE IF NOT EXISTS raw_cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    price TEXT,
                    mileage TEXT,
                    url TEXT,
                    year TEXT,
                    place TEXT,
                    raw_json TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            c.execute(sql)
            conn.commit()
            logger.info("Database initialized successfully")

    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise


def insert_raw_cars(cars: List[Dict[str, Any]]) -> None:
    if not cars:
        logger.info("No cars to insert")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            car_data = [
                (
                    car.get("title"),
                    car.get("price"),
                    car.get("mileage"),
                    car.get("url"),
                    car.get("year"),
                    car.get("place"),
                    json.dumps(car),
                )
                for car in cars
            ]

            c.executemany(
                """
                INSERT INTO raw_cars (title, price, mileage, url, year, place, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                car_data,
            )
            conn.commit()
            logger.info(f"Successfully inserted {len(cars)} cars into the database")

    except sqlite3.Error as e:
        logger.error(f"Database insertion error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error preparing car data for insertion: {e}")
        raise


def process_occasions_to_cars(occasions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert occasions data to car records."""
    raw_cars = []

    for occ in occasions:
        try:
            other_portal = next(
                (p for p in occ.get("portals", []) if p.get("type") == "other"), None
            )

            car_data = {
                "title": occ.get("title"),
                "price": occ.get("price"),
                "mileage": occ.get("km"),
                "url": other_portal.get("url") if other_portal else None,
                "year": occ.get("year"),
                "place": occ.get("place"),
            }

            raw_cars.append(car_data)

        except Exception as e:
            logger.warning(f"Error processing occasion: {e}, skipping this record")
            continue

    return raw_cars


def scrape_and_save_raw(url: str, cookies: dict) -> bool:
    try:
        html = fetch_html_with_cookie(url, cookies)
        if not html:
            logger.error("Failed to fetch HTML content")
            return False

        occasions = extract_raw_data_from_html(html)
        if not occasions:
            logger.warning("No occasions extracted from HTML")
            return False

        raw_cars = process_occasions_to_cars(occasions)
        if not raw_cars:
            logger.warning("No cars processed from occasions")
            return False

        init_db()
        insert_raw_cars(raw_cars)
        logger.info(f"Successfully scraped and saved {len(raw_cars)} cars")
        return True

    except Exception as e:
        logger.error(f"Error in scrape_and_save_raw: {e}")
        return False
