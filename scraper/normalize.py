import json
from typing import List, Dict, Any


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

RAW_JSON = "raw_cars.json"
OUTPUT_JSON = "gaspedaal_cars.json"


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
        **raw_car,
        "name": name,
        "priceNum": price_num,
        "mileageNum": mileage_num,
        "plate": plate,
        "apkExpiry": get_apk_expiry_from_rdw(normalize_plate),
        "finnikUrl": finnik_url,
        "estimatedPrice": estimated_price,
    }


def normalize_and_save(cookies: dict) -> None:
    with open(RAW_JSON, "r", encoding="utf-8") as f:
        raw_cars = json.load(f)
    normalize_cars = [normalize_car_data(car, cookies) for car in raw_cars]
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(normalize_cars, f, ensure_ascii=False, indent=2)
    print(f"Normalized {len(normalize_cars)} cars. Saved to {OUTPUT_JSON}.")
