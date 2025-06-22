import openai
import os
import aiohttp
import asyncio

from helpers import(
    normalize_plate_number,
    fetch_html,
    get_Finnik_page    
)

openai.api_key = os.getenv("DEEPSEEK_API_KEY")
openai.base_url = "https://api.deepseek.com"

RDW_ENDPOINTS = {
    "voertuigInfo": "https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={plate}",
    "assenInfo": "https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken={plate}",
    "brandstofInfo": "https://opendata.rdw.nl/resource/8n4e-qkew.json?kenteken={plate}",
    "carrosserieInfo": "https://opendata.rdw.nl/resource/vezc-m2t6.json?kenteken={plate}",
    "voertuigklasseInfo": "https://opendata.rdw.nl/resource/95zd-6z5x.json?kenteken={plate}",
}

async def fetch_json(session, url):
    async with session.get(url, timeout=10) as resp:
        if resp.status == 200:
            return await resp.json()
        return {}

async def search(plate):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_json(session, RDW_ENDPOINTS["voertuigInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["assenInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["brandstofInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["carrosserieInfo"].format(plate=plate)),
            fetch_json(session, RDW_ENDPOINTS["voertuigklasseInfo"].format(plate=plate)),
        ]
        voertuigInfo, assenInfo, brandstofInfo, carrosserieInfo, voertuigklasseInfo = await asyncio.gather(*tasks)
        return {
            "voertuigInfo": voertuigInfo,
            "assenInfo": assenInfo,
            "brandstofInfo": brandstofInfo,
            "carrosserieInfo": carrosserieInfo,
            "voertuigklasseInfo": voertuigklasseInfo,
        }

async def fetch_rdw_data(normalize_plate):
    return await search(normalize_plate)
    

def fetch_finnik_html(normalize_plate):
    url = get_Finnik_page(normalize_plate)
    html = fetch_html(url)
    return (html)

def get_llm_summary(car,rdw_data, finnik_html):
    prompt = f"""你是一个专业的荷兰二手车分析助手,请分析以下二手车信息，并用中文简要总结其优缺点和购买建议:
1. 车辆基本信息:
{json.dumps(car, ensure_ascii=False, indent=2)}

2. RDW 数据:
{json.dumps(rdw_data, ensure_ascii=False, indent=2)}

3. Finnik 页面HTML:
{finnik_html}
请简要总结。"""
    try:
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM summary error: {e}")
        return ""

    
if __name__ == "__main__":
    car = 
    plate = normalize_plate_number("H-401-ZX")
    rdw_data =  asyncio.run(fetch_rdw_data(plate))
    finnik_html = fetch_finnik_html(plate)
    summary = get_llm_summary(car, rdw_data, finnik_html)
    print(summary)


