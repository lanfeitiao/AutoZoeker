import aiohttp
from typing import Any, Dict
import asyncio


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
