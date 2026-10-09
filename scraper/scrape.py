import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from datetime import datetime

CARS = [
    ("پژو 207", "https://bama.ir/car/peugeot-207/all-models/all-trims"),
    ("دنا پلاس", "https://bama.ir/car/dena-plus/all-models/all-trims"),
    ("تارا", "https://bama.ir/car/tara/all-models/all-trims"),
    ("رانا پلاس", "https://bama.ir/car/rana-plus/all-models/all-trims"),
    ("سورن", "https://bama.ir/car/samand/all-models/all-trims"),
    ("هایما S7", "https://bama.ir/car/haima-s7/all-models/all-trims"),
    ("ری را", "https://bama.ir/car/ri-ra/all-models/all-trims"),
    ("شاهین", "https://bama.ir/car/shahin/all-models/all-trims"),
    ("کوییک", "https://bama.ir/car/quick/all-models/all-trims"),
    ("ساینا", "https://bama.ir/car/saina/all-models/all-trims"),
    ("اطلس", "https://bama.ir/car/atlas/all-models/all-trims"),
    ("سهند", "https://bama.ir/car/sahand/all-models/all-trims"),
    ("کارون", "https://bama.ir/car/karoon/all-models/all-trims"),
    ("زامیاد", "https://bama.ir/car/zamyad/all-models/all-trims"),
    ("آریسان", "https://bama.ir/car/arisun/all-models/all-trims"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fa-IR,fa;q=0.9",
}

def extract_prices(html):
    soup = BeautifulSoup(html, "html.parser")
    prices = []
    text = soup.get_text()
    matches = re.findall(r'([\d,]{9,})\s*تومان', text)
    for m in matches:
        try:
            price = int(m.replace(',', ''))
            if 100000000 < price < 50000000000:
                prices.append(price)
        except:
            continue
    if not prices:
        return None
    return {
        "min": min(prices),
        "max": max(prices),
        "avg": sum(prices) // len(prices),
        "count": len(prices),
    }

def main():
    results = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "source": "bama.ir",
        "cars": {}
    }
    
    for car_name, url in CARS:
        try:
            print(f"Getting {car_name}...")
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                data = extract_prices(r.text)
                if data:
                    results["cars"][car_name] = data
                    print(f"  OK - {data['count']} listings")
            time.sleep(3)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    os.makedirs("data", exist_ok=True)
    with open("data/prices.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Saved: {len(results['cars'])} cars")

if __name__ == "__main__":
    main()
