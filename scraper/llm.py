import openai
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Any, Dict
import json
from dotenv import load_dotenv
from helpers import normalize_plate_number
from finnik import fetch_finnik_html

load_dotenv()
openai.api_key = os.getenv("DEEPSEEK_API_KEY")
openai.base_url = "https://api.deepseek.com"

RDW_ENDPOINTS = {
    "voertuigInfo": "https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={plate}",
    "assenInfo": "https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken={plate}",
    "brandstofInfo": "https://opendata.rdw.nl/resource/8n4e-qkew.json?kenteken={plate}",
    "carrosserieInfo": "https://opendata.rdw.nl/resource/vezc-m2t6.json?kenteken={plate}",
    "voertuigklasseInfo": "https://opendata.rdw.nl/resource/95zd-6z5x.json?kenteken={plate}",
}


async def fetch_json(session: Any, url: str) -> Dict:
    async with session.get(url, timeout=10) as resp:
        if resp.status == 200:
            return await resp.json()
        return {}


async def search(plate: str) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_json(session, RDW_ENDPOINTS["voertuigInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["assenInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["brandstofInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["carrosserieInfo"].format(plate=plate)),
            fetch_json(
                session, RDW_ENDPOINTS["voertuigklasseInfo"].format(plate=plate)
            ),
        ]
        voertuigInfo, assenInfo, brandstofInfo, carrosserieInfo, voertuigklasseInfo = (
            await asyncio.gather(*tasks)
        )
        return {
            "voertuigInfo": voertuigInfo,
            "assenInfo": assenInfo,
            "brandstofInfo": brandstofInfo,
            "carrosserieInfo": carrosserieInfo,
            "voertuigklasseInfo": voertuigklasseInfo,
        }


async def fetch_rdw_data(normalize_plate: str) -> Dict[str, Any]:
    return await search(normalize_plate)


def sanitize_html(html: str) -> str:
    """
    Remove all attributes from HTML tags, preserving only tag structure and text.
    Returns the sanitized inner HTML of the <body> element.
    """
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        root = soup.body or soup

        for tag in root.find_all(True):
            tag.attrs = {}
        return "".join(str(child) for child in root.contents)

    except Exception as e:
        print(f"Error sanitizing HTML: {e}")
        return ""


def get_llm_summary(
    car: Dict[str, Any], rdw_data: Dict[str, Any], finnik_html: str
) -> str:
    sanitize_finnik = sanitize_html(finnik_html)
    prompt = f"""
You are a professional Dutch used-car data analysis assistant.
Please analyze the following information about a used car from three different sources:

1. **Car listing details** (e.g. price, mileage, estimated_price):
{json.dumps(car, ensure_ascii=False, indent=2)}

2. **RDW data** (official Dutch vehicle database):
{json.dumps(rdw_data, ensure_ascii=False, indent=2)}

3. **Finnik page HTML**:
{sanitize_finnik}

Please pay special attention to key indicators such as the vehicle's year of manufacture, 
first registration date, APK (MOT) expiration date, mileage, ownership history, and fault history.
Based on your professional experience, you may also evaluate any other important data.

Please respond in English, stating whether it is worth purchasing, explaining your reasoning, 
and giving a price recommendation.

"""
    try:
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM summary error: {e}")
        return ""


if __name__ == "__main__":
    plate = normalize_plate_number("H-401-ZX")
    rdw_data = asyncio.run(fetch_rdw_data(plate))
    finnik_html = fetch_finnik_html(plate)
    with open("finnik.html", "w") as f:
        f.write(finnik_html)
    with open("rdw_data.md", "w") as f:
        f.write(json.dumps(rdw_data, ensure_ascii=False, indent=2))
    car = "gaspedaal_cars.json"
    summary = get_llm_summary(car, rdw_data, finnik_html)
    print(summary)
