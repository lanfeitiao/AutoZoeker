import sys
from scrape import scrape_and_save_raw
from normalize import normalize_and_save

url = (
    "https://www.gaspedaal.nl/toyota/corolla/stationwagon"
    "?brnst=25&bmin=2020&pmax=20000&kmax=120000&srt=df-a"
)
# Will expire monthly
cookies = {"authId": "8a8ec16c-8399-4950-acea-7e8458b25c9e"}


if __name__ == "__main__":
    if "scrape" in sys.argv:
        scrape_and_save_raw(url, cookies)
    if "normalize" in sys.argv:
        normalize_and_save(cookies)
