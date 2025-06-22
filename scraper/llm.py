import openai
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from bs4 import NavigableString, Tag
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
    try:
        soup = BeautifulSoup(html, "html.parser")
        body = soup.body
        if not body:
            return ""

        new_soup = BeautifulSoup("<div></div>", "html.parser")
        container = new_soup.div

        def copy_node(node, parent):
            if isinstance(node, NavigableString):
                parent.append(node)
            elif isinstance(node, Tag):
                new_tag = new_soup.new_tag(node.name)
                parent.append(new_tag)
                for child in node.contents:
                    copy_node(child, new_tag)

        for child in body.contents:
            copy_node(child, container)

        return container.decode_contents()

    except Exception as e:
        print(f"Error sanitizing HTML: {e}")
        return ""


def get_llm_summary(
    car: Dict[str, Any], rdw_data: Dict[str, Any], finnik_html: str
) -> str:
    sanitize_finnik = sanitize_html(finnik_html)
    prompt = f"""
You are a professional Dutch used-car analyst. Please review the information below and 
give a short summary of the car's pros, cons, and buying advice.

1. Car details:
{json.dumps(car, ensure_ascii=False, indent=2)}

2. RDW data:
{json.dumps(rdw_data, ensure_ascii=False, indent=2)}

3. Finnik page HTML:
{sanitize_finnik}

Keep the summary brief and use concise English.
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
    car = "gaspedaal_cars.json"
    summary = get_llm_summary(car, rdw_data, finnik_html)
    print(summary)
