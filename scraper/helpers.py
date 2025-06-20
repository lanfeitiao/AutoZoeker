import re
from bs4 import BeautifulSoup
import requests

def normalize_plate_number(plate):
    if not plate:
        return None
    return plate.replace('-', '').upper()

def extract_model_name(text):
    """Extracts the real model name like '1.8 Hybrid Active' from a string."""
    endings = [
        "Active", "Business Plus", "Business", "Comfort", "Executive", "Dynamic", "Premium", "Plus"
    ]
    endings_sorted = sorted(endings, key=len, reverse=True)
    ending_pattern = "|".join([re.escape(e) for e in endings_sorted])
    pattern = rf"(\d\.\d\s*Hybrid(?:\s+[A-Za-z]+)*\s(?:{ending_pattern}))"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

def fetch_html_with_cookie(url, cookies):
    response = requests.get(url, cookies=cookies, timeout=15)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None

    
def fetch_url(url,expect_json=False):
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        return response.json() if expect_json else response.text
    else:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None

def extract_plate_from_url(url, cookies):
    html=fetch_html_with_cookie(url,cookies)
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

def get_apk_expiry_from_rdw(normalize_plate):
    url = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={normalize_plate}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and 'vervaldatum_apk' in data[0]:
                raw = data[0]['vervaldatum_apk']
                return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    except Exception as e:
        print(f"Error fetching APK for {normalize_plate}: {e}")
    return None

def get_Finnik_page(normalize_plate):
    url = f"https://finnik.nl/kenteken/{normalize_plate}/gratis"
    return url

def get_version_name_from_finnik(original_name, plate):
    url   = "https://finnik.nl/kenteken/"
    params = {"licensePlateNumber": plate}
    headers = {"User-Agent": "Mozilla/5.0"}  
    resp = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    version_name = None
    for row in soup.select(".row"):
        label = row.select_one(".label")
        if label and "Uitvoering" in label.get_text(strip=True):
            version_name = row.select_one(".value").get_text(strip=True)
            break
    if version_name:
        return version_name 
    return original_name
