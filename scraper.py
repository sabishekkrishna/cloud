import os
import re
import requests
from bs4 import BeautifulSoup

# Load variables from GitHub Secrets / Local Env
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Valid Cubelelo product URL format: https://www.cubelelo.com/products/<product-name>
URL = "https://www.cubelelo.com/products/moyu-rs3m-v5-se-magnetic"
TARGET_PRICE = 5000.0  # Set your target alert price threshold in ₹

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set. Skipping notification.")
        return
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(telegram_url, json=payload)
    print("Telegram Notification Status Code:", response.status_code)

def scrape_cubelelo_price():
    # Method 1: Direct Shopify JSON API (Fast & Reliable)
    try:
        json_url = f"{URL}.json"
        res = requests.get(json_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            variants = data.get("product", {}).get("variants", [])
            if variants:
                price = float(variants[0]["price"])
                print(f"Extracted price via Shopify API: ₹{price}")
                return price
    except Exception as e:
        print(f"JSON API fetch fallback: {e}")

    # Method 2: HTML Meta Tag Parsing (Fallback)
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract from og:price:amount meta tag
        meta_price = soup.find("meta", property=re.compile(r"price:amount"))
        if meta_price and meta_price.get("content"):
            price = float(meta_price["content"])
            print(f"Extracted price from meta tag: ₹{price}")
            return price

    except Exception as e:
        print(f"Error during scraping: {e}")

    print("No price element matched on Cubelelo product page.")
    return None

if __name__ == "__main__":
    current_price = scrape_cubelelo_price()
    print(f"Scraped Price: {current_price}")
    
    if current_price is not None:
        if current_price <= TARGET_PRICE:
            alert_msg = (
                f"🚨 *PRICE DROP ALERT!*\n\n"
                f"Item: *MoYu RS3M V5*\n"
                f"Current Price: *₹{current_price}*\n"
                f"Target Price: ₹{TARGET_PRICE}\n\n"
                f"[Buy on Cubelelo]({URL})"
            )
            send_telegram_alert(alert_msg)
        else:
            print(f"Current price ₹{current_price} is above target threshold ₹{TARGET_PRICE}.")