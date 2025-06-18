import json
from bs4 import BeautifulSoup
import time

from helpers import extract_model_name, extract_plate_from_url, fetch_html

url = (
    "https://www.gaspedaal.nl/toyota/corolla/stationwagon"
    "?brnst=25&bmin=2020&pmax=20000&kmax=120000&srt=df-a"
)
cookies = {"authId": "8a8ec16c-8399-4950-acea-7e8458b25c9e"}        

OUTPUT_JSON = "gaspedaal_cars.json"

def extract_cars_from_html(html):
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

    cars = []
    for occ in occasions:
        other_portal = next((p for p in occ.get("portals", []) if p.get("type") == "other"), None)
        model_source = occ.get("version") or occ.get("title")
        name = extract_model_name(model_source)
        car = {
            "name": name,
            "price": occ.get("price"),
            "year": occ.get("year"),
            "mileage": occ.get("km"),
            "place": occ.get("place"),
            "url": other_portal["url"] if other_portal else None,
            "plate": extract_plate_from_url(other_portal["url"], cookies)
        }
        cars.append(car)
        time.sleep(1)
    return cars

if __name__ == "__main__":
    html = fetch_html(url,cookies)
    cars = extract_cars_from_html(html)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(cars)} cars. Saved to {OUTPUT_JSON}.") 