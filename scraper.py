import os
import re
import requests
from bs4 import BeautifulSoup

# Load variables from environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Cubelelo Product URL & Target Threshold
URL = "https://www.cubelelo.com/collections/bestsellers/products/rs3m-v5-3x3-cube-magnetic-dual-adjustment"
TARGET_PRICE = 9999.0  # Set your desired alert price in INR (₹)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def send_telegram_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(telegram_url, json=payload)
    print("Telegram Notification Status:", response.status_code)

def scrape_cubelelo_price():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Cubelelo / Shopify DOM price selectors
        price_selectors = [
            "span.price-item--sale",
            "span.price-item--regular",
            ".product__price .price-item",
            ".price-item",
            "span.price-item"
        ]

        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_raw = price_element.get_text().strip()
                # Clean currency symbols (₹, Rs, commas)
                clean_price = re.sub(r'[^\d.]', '', price_raw.replace(',', ''))
                if clean_price:
                    print(f"Extracted price using selector '{selector}': ₹{clean_price}")
                    return float(clean_price)

        print("No price element matched on Cubelelo product page.")
    except Exception as e:
        print(f"Error during scraping: {e}")
    return None

if __name__ == "__main__":
    current_price = scrape_cubelelo_price()
    print(f"Scraped Price: {current_price}")
    
    if current_price is not None:
        if current_price <= TARGET_PRICE:
            alert_msg = (
                f"🚨 *CUBELELO PRICE DROP ALERT!*\n\n"
                f"Item: *MoYu RS3M V5 3x3*\n"
                f"Current Price: *₹{current_price}*\n"
                f"Target Price: ₹{TARGET_PRICE}\n\n"
                f"[Buy on Cubelelo]({URL})"
            )
            send_telegram_alert(alert_msg)
        else:
            print(f"Current price ₹{current_price} is above target ₹{TARGET_PRICE}.")