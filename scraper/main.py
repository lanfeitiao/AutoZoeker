import json
from bs4 import BeautifulSoup
import requests

url = (
    "https://www.gaspedaal.nl/toyota/corolla/stationwagon"
    "?brnst=25&bmin=2020&pmax=20000&kmax=120000&srt=df-a"
)

cookies = {"authId": "8a8ec16c-8399-4950-acea-7e8458b25c9e"}

resp = requests.get(url, cookies=cookies, timeout=20)
resp.raise_for_status()         
html = resp.text  

OUTPUT_JSON = "cars_from_next_data.json"

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
        # Find the first portal with type 'other'
        other_portal = next((p for p in occ.get("portals", []) if p.get("type") == "other"), None)
        car = {
            "version": occ.get("version"),
            "price": occ.get("price"),
            "year": occ.get("year"),
            "km": occ.get("km"),
            "place": occ.get("place"),
            "url": other_portal["url"] if other_portal else None
        }
        cars.append(car)
    return cars

if __name__ == "__main__":
    cars = extract_cars_from_html(html)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(cars)} cars. Saved to {OUTPUT_JSON}.") 