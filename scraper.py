import os
import re
import requests
from bs4 import BeautifulSoup

# Load variables from environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Target configuration
URL = "https://www.amazon.in/dp/B0DDV1GWP7"  # Replace with your target ASIN URL
TARGET_PRICE = 999999.0  # Temporarily high threshold for testing

# Anti-bot browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1"
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

def scrape_amazon_price():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status: {response.status_code}")
            return None
        
        # Check if Amazon served a Bot Check / CAPTCHA page
        if "captcha" in response.text.lower() or "robot check" in response.text.lower():
            print("Amazon served a CAPTCHA / Bot Check page to GitHub IP!")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Fallback list of Amazon price CSS selectors
        price_selectors = [
            "#corePrice_feature_div .a-offscreen",
            ".a-price .a-offscreen",
            "span.a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".apexPriceToPay .a-offscreen"
        ]

        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_raw = price_element.get_text().strip()
                clean_price = re.sub(r'[^\d.]', '', price_raw.replace(',', ''))
                if clean_price:
                    print(f"Extracted price using selector '{selector}': {clean_price}")
                    return float(clean_price)

        print("No price element matched the selectors on this page.")
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
            print(f"Price ₹{current_price} is higher than target ₹{TARGET_PRICE}.")