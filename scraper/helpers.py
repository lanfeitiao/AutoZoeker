import re
from bs4 import BeautifulSoup
import requests

def normalize_plate_number(plate):
    return plate.replace('-', '').upper()

def extract_model_name(text):
    """Extracts the real model name like '1.8 Hybrid Active' from a string."""
    if not text:
        return None
    # Try to find a pattern like '1.8 Hybrid Active' or '2.0 Hybrid Dynamic' etc.
    match = re.search(r'(\d\.\d\s*Hybrid\s*[A-Za-z]+)', text)
    if match:
        return match.group(1).strip()
    # Fallback: try to find 'Hybrid' and the word after
    match = re.search(r'(Hybrid\s*[A-Za-z]+)', text)
    if match:
        return match.group(1).strip()
    return text.strip()

def fetch_html(url, cookies):
    response = requests.get(url, cookies=cookies, timeout=15)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None

def extract_plate_from_url(url, cookies):
    html=fetch_html(url,cookies)
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
