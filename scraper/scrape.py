import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
import statistics
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    "Referer": "https://bama.ir/",
}

def extract_prices(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # حذف بخش‌های جانبی که قیمت‌های نامرتبط دارن
    for tag in soup.find_all(['aside', 'footer', 'nav', 'header']):
        tag.decompose()
    for cls in ['sidebar', 'recommendation', 'related', 'similar', 'footer', 'header', 'menu']:
        for tag in soup.find_all(class_=re.compile(cls, re.I)):
            tag.decompose()
    
    prices = []
    
    # روش ۱: المان‌های قیمت (کلاس price)
    price_elements = soup.find_all(class_=re.compile(r'price|قیمت', re.I))
    for el in price_elements:
        text = el.get_text(strip=True)
        match = re.search(r'([\d,]{9,})', text)
        if match:
            try:
                p = int(match.group(1).replace(',', ''))
                if 200000000 < p < 20000000000:
                    prices.append(p)
            except:
                pass
    
    # روش ۲: regex روی متن
    if len(prices) < 5:
        text = soup.get_text()
        matches = re.findall(r'([\d,]{9,})\s*تومان', text)
        for m in matches:
            try:
                p = int(m.replace(',', ''))
                if 200000000 < p < 20000000000:
                    prices.append(p)
            except:
                pass
    
    if len(prices) < 3:
        return None
    
    # فیلتر کردن outliers با استفاده از IQR
    prices.sort()
    n = len(prices)
    q1_idx = n // 4
    q3_idx = 3 * n // 4
    filtered = prices[q1_idx:q3_idx] if q3_idx > q1_idx else prices
    
    median_price = int(statistics.median(filtered))
    
    return {
        "min": min(filtered),
        "max": max(filtered),
        "avg": median_price,       # برای سازگاری با نسخه قبل
        "median": median_price,    # مقدار واقعی که استفاده می‌شه
        "count": len(prices),
        "filtered_count": len(filtered),
    }

def main():
    results = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "source": "bama.ir",
        "cars": {}
    }
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for car_name, url in CARS:
        try:
            print(f"Getting {car_name}...")
            r = session.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                data = extract_prices(r.text)
                if data:
                    results["cars"][car_name] = data
                    print(f"  OK - {data['count']} listings, median {data['median']:,}")
                else:
                    print(f"  NO PRICES")
            else:
                print(f"  HTTP {r.status_code}")
            time.sleep(4)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    os.makedirs("data", exist_ok=True)
    with open("data/prices.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved: {len(results['cars'])} cars")

if __name__ == "__main__":
    main()
