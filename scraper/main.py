import json
from bs4 import BeautifulSoup
import time

from helpers import (
    fetch_html,
    extract_model_name,
    extract_plate_from_url,
    normalize_plate_number,
    get_apk_expiry_from_rdw,
    get_Finnik_page
)

url = (
    "https://www.gaspedaal.nl/toyota/corolla/stationwagon"
    "?brnst=25&bmin=2020&pmax=20000&kmax=120000&srt=df-a"
)

# Will expire monthly
cookies = {"authId": "8a8ec16c-8399-4950-acea-7e8458b25c9e"}        

OUTPUT_JSON = "gaspedaal_cars.json"

def extract_raw_cars_from_html(html):
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

def normalize_car_data(occ, cookies):
    other_portal = next((p for p in occ.get("portals", []) if p.get("type") == "other"), None)
    model_source = occ.get("version") or occ.get("title")
    name = extract_model_name(model_source)
    price_str = str(occ.get("price") or "0")
    price_num = int(''.join(filter(str.isdigit, price_str))) if price_str else 0
    mileage_str = str(occ.get("km") or "0")
    mileage_num = int(''.join(filter(str.isdigit, mileage_str))) if mileage_str else 0
    url = other_portal["url"] if other_portal else None
    plate = extract_plate_from_url(url, cookies)
    normalize_plate = normalize_plate_number(plate)
    return {
        "name": name,
        "price": price_str,        
        "priceNum": price_num,    
        "year": occ.get("year"),
        "mileage": mileage_str,     
        "mileageNum": mileage_num,  
        "place": occ.get("place"),
        "url": url,
        "plate": plate,
        "apkExpiry": get_apk_expiry_from_rdw(normalize_plate),
        "finnikUrl": get_Finnik_page(normalize_plate)
    }

if __name__ == "__main__":
    html = fetch_html(url, cookies)
    raw_cars = extract_raw_cars_from_html(html)
    cars = [normalize_car_data(occ, cookies) for occ in raw_cars]
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(cars)} cars. Saved to {OUTPUT_JSON}.") 