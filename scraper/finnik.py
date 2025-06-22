import requests
from bs4 import BeautifulSoup


def get_Finnik_page(normalize_plate: str) -> str:
    url = f"https://finnik.nl/kenteken/{normalize_plate}/gratis"
    return url


def fetch_finnik_html(plate: str) -> str:
    """
    Helper to fetch the raw HTML from Finnik for a given license plate.
    """
    url = "https://finnik.nl/kenteken/"
    params = {"licensePlateNumber": plate}
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()

    return resp.text


def get_version_name_from_finnik(original_name: str, plate: str) -> str:
    """
    Retrieve the 'Uitvoering' (version name) from Finnik for a given plate
    by parsing the raw HTML.
    Falls back to original_name if not found.
    """
    html = fetch_finnik_html(plate)
    soup = BeautifulSoup(html, "html.parser")

    for row in soup.select(".row"):
        label = row.select_one(".label")
        if label and "Uitvoering" in label.get_text(strip=True):
            return row.select_one(".value").get_text(strip=True)

    return original_name
