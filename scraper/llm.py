from openai import OpenAI
import os
import asyncio
from bs4 import BeautifulSoup
import json
from typing import Tuple, Any, Dict
import re
from dotenv import load_dotenv
from helpers import normalize_plate_number
from finnik import fetch_finnik_html
from rdw import fetch_rdw_data

load_dotenv()
# openai.api_key = os.getenv("DEEPSEEK_API_KEY")
# openai.base_url = "https://api.deepseek.com"


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


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def build_car_analysis_prompt(
    car: Dict[str, Any], rdw_data: Dict[str, Any], finnik_html: str
) -> str:
    """
    Construct the system prompt for the analysis.
    """
    sanitized = sanitize_html(finnik_html)
    return f"""
Please analyze the following information about a used car from three different sources:

1. Car listing details (price, mileage, estimated_price, etc.):
{json.dumps(car, ensure_ascii=False, indent=2)}

2. RDW data (official Dutch vehicle database):
{json.dumps(rdw_data, ensure_ascii=False, indent=2)}

3. Finnik page HTML (sanitized):
{sanitized}

Pay special attention to:
- Year of manufacture
- First registration date
- APK (MOT) expiration date
- Mileage
- Price difference between estimated_price and selling price
- Ownership history
- Fault or damage history

Based on your professional experience, evaluate whether it's worth purchasing,
explain your reasoning, and give an evaluation score out of 100.

Please structure your analysis in the following sections:
    1. Vehicle Overview
    2. Price Analysis
    3. History & Maintenance
    4. Risk Factors
    5. Final Recommendation
    
Use the report_summary tool to provide your analysis and score.
"""


def get_report_summary_tool() -> Dict[str, Any]:
    """
    Returns the tool definition for Deepseek function-calling.
    """
    return {
        "type": "function",
        "function": {
            "name": "report_summary",
            "description": "Produces a car-buying recommendation and score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "llm_summary": {"type": "string"},
                    "llm_score": {"type": "integer"},
                },
                "required": ["llm_summary", "llm_score"],
            },
        },
    }


def send_messages(messages: list[dict], tools) -> Any:
    """
    Wrapper around Deepseek chat completion.
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )
    return response.choices[0].message


def parse_llm_response(message: Any) -> Tuple[str, int]:
    """
    Extract llm_summary and llm_score from tool call or fallback JSON.
    """
    # Attempt function-calling response
    tool_calls = message.tool_calls
    if tool_calls:
        call = tool_calls[0]
        raw_args = call.function.arguments or ""
    else:
        # Fallback to plain content JSON
        raw_args = message.content or ""
    data = json.loads(raw_args)
    return data["llm_summary"], data["llm_score"]


def get_llm_summary(
    norm_car: Dict[str, Any],
) -> Tuple[str, int]:
    """
    Orchestrates prompt building, API call, and response parsing.
    Returns (summary, score).
    """
    tools = [get_report_summary_tool()]
    plate = normalize_plate_number(norm_car["plate"])
    rdw_data = asyncio.run(fetch_rdw_data(plate))
    finnik_html = fetch_finnik_html(plate)
    system_msg = {
        "role": "system",
        "content": "You are a professional Dutch used-car data analysis assistant.",
    }
    user_msg = {
        "role": "user",
        "content": build_car_analysis_prompt(norm_car, rdw_data, finnik_html),
    }

    try:
        message = send_messages([system_msg, user_msg], tools)
        return parse_llm_response(message)
    except Exception as e:
        print(f"Error in LLM processing: {e}")
        return "Unable to generate summary.", 0


if __name__ == "__main__":
    with open("gaspedaal_cars.json", "r", encoding="utf-8") as f:
        cars = json.load(f)
    norm_car = next(car for car in cars if car.get("plate") == "H-401-ZX")
    summary = get_llm_summary(norm_car)
    print(summary)
