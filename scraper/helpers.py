import re
from typing import Optional, Any, Dict
from bs4 import BeautifulSoup
import requests


def normalize_plate_number(plate: Optional[str]) -> Optional[str]:
    if not plate:
        return None
    return plate.replace("-", "").upper()


def extract_model_name(text: Optional[str]) -> Optional[str]:
    """Extracts the real model name like '1.8 Hybrid Active' from a string."""
    if not text:
        return None
    endings = [
        "Active",
        "Business Plus",
        "Business",
        "Comfort",
        "Executive",
        "Dynamic",
        "Premium",
        "Plus",
    ]
    endings_sorted = sorted(endings, key=len, reverse=True)
    ending_pattern = "|".join([re.escape(e) for e in endings_sorted])
    pattern = rf"(\d\.\d\s*Hybrid(?:\s+[A-Za-z]+)*\s(?:{ending_pattern}))"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()


def fetch_html_with_cookie(url: str, cookies: dict) -> Optional[str]:
    response = requests.get(url, cookies=cookies, timeout=15)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None


def fetch_url(url: str, expect_json: bool = False) -> Any:
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        return response.json() if expect_json else response.text
    else:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None


def extract_plate_from_url(url: Optional[str], cookies: dict) -> Optional[str]:
    html = fetch_html_with_cookie(url, cookies)
    # ① data-testid
    m = re.search(r'data-testid="svg-Kenteken-([^"]+)"', html)
    if m:
        return m.group(1).strip()

    soup = BeautifulSoup(html, "html.parser")
    # ② <td>Kenteken</td><td>...</td>
    cell = soup.find("td", string=lambda t: t and t.strip().lower() == "kenteken")
    if cell and (val := cell.find_next_sibling("td")):
        return val.get_text(strip=True)
    return None


def get_apk_expiry_from_rdw(normalize_plate: str) -> Optional[str]:
    url = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={normalize_plate}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and "vervaldatum_apk" in data[0]:
                raw = data[0]["vervaldatum_apk"]
                return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    except Exception as e:
        print(f"Error fetching APK for {normalize_plate}: {e}")
    return None


def clean_url(raw_url: Optional[str]) -> Optional[str]:
    """
    Normalize placeholder URLs (e.g. 'N/A', empty strings)
    into a real None, so they become SQL NULL.
    """
    if not raw_url:
        return None
    cleaned = raw_url.strip()
    if cleaned.upper() in ("N/A", "NONE", "-"):
        return None
    return cleaned
