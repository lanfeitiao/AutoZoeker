import re
import requests
from helpers import fetch_url
from typing import Optional, Dict, Any

API_BASE = "https://api.anwb.nl/car-information/backend-application/api/v0"


def get_configuration_url(plate: str) -> Optional[Any]:
    config_url = f"{API_BASE}/licensePlate/{plate}"
    data = fetch_url(config_url, expect_json=True)
    return data


def get_configuration_data(plate: str, name: str) -> Optional[Dict[str, Any]]:
    name_clean = name.upper()
    words = re.findall(r"\b[A-ZÀ-ÖØ-Ý]+\b", name_clean)
    synonyms = {
        "HYBRID": "HEV",
    }
    url = get_configuration_url(plate)
    if url is None:
        return None
    for item in url:
        cfg_name = item["configuration"]["name"].upper()
        ok = True
        for w in words:
            if w in cfg_name:
                continue
            syn = synonyms.get(w)
            if syn and syn in cfg_name:
                continue
            ok = False
            break
        if ok:
            return item
    return None


def get_ratelist_json(
    data: Optional[Dict[str, Any]], mileage: int, plate: str
) -> Optional[Dict[str, Any]]:
    if data is None:
        return None
    cfg = data["configuration"]["id"]
    costs = data["costs"]
    hist = data["history"]

    original_price = costs["originalListPrice"]
    options_price = costs["optionsPrice"]

    month, year = hist["firstInternationalAdmission"].split("/")

    url = f"{API_BASE}/configuration/{cfg}/ratelist"
    params = {
        "mileage": int(mileage),
        "configurationId": cfg,
        "licensePlateYear": int(year),
        "licensePlateMonth": int(month),
        "newPrice": int(original_price),
        "licensePlate": plate,
        "optionsPrice": int(options_price),
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    rate = resp.json()
    return rate


def get_rijklaarprijs(mileage: int, plate: str, name: str) -> Optional[int]:
    data = get_configuration_data(plate, name)
    rate = get_ratelist_json(data, mileage, plate)
    if rate is None:
        return None
    rijklaarprijs = next(
        (
            entry["amount"]
            for entry in rate["lists"]
            if entry["name"] == "Rijklaarprijs"
        ),
        None,
    )
    return rijklaarprijs
