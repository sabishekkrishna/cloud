import os
import re
import json
import requests
from bs4 import BeautifulSoup

# Load variables from environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Product configuration
URL = "https://www.amazon.in/dp/B0DDV1GWP7"  # Replace with target ASIN URL
TARGET_PRICE = 1000.00  # Set target threshold

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
    print("Telegram Notification Sent:", response.status_code)

def scrape_amazon_price():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch page. HTTP Status: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Scrape price element from Amazon DOM
        price_span = soup.find("span", {"class": "a-offscreen"})
        if price_span:
            price_raw = price_span.get_text()
            # Clean non-numeric characters (commas, currency symbols)
            clean_price = re.sub(r'[^\d.]', '', price_raw.replace(',', ''))
            return float(clean_price)
    except Exception as e:
        print(f"Error during scraping: {e}")
    return None

if __name__ == "__main__":
    current_price = scrape_amazon_price()
    print(f"Scraped Price: {current_price}")
    
    if current_price is not None:
        if current_price <= TARGET_PRICE:
            alert_msg = (
                f"🚨 *PRICE DROP ALERT!*\n\n"
                f"Current Price: *₹{current_price}*\n"
                f"Target Price: ₹{TARGET_PRICE}\n\n"
                f"[View Product on Amazon]({URL})"
            )
            send_telegram_alert(alert_msg)
        else:
            print(f"Price ₹{current_price} is still above target ₹{TARGET_PRICE}.")