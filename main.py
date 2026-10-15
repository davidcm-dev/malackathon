import os
import re
import time
import cv2
from dotenv import load_dotenv
from playwright.sync_api import expect, sync_playwright
import pytesseract
import requests
import re

load_dotenv()


def setup_browser(p):
    # Launch Firefox (system binary path is optional)
    browser = p.firefox.launch(
        headless=False
    )

    context = browser.new_context(
        extra_http_headers={
            "x-obg-trusted-traffic": "1",
            "x-obg-country-code": "ES",
            "x-obg-origin": "ES",
            "x-obg-internal": "1",
        }
    )

    page = context.new_page()

    # 1. Navigate to the domain first so localStorage belongs to the correct origin
    page.goto("https://www.betsson.es/casino/tragaperras-slots/bubble-up?gameAction=play")

    # 2. Inject all localStorage keys in a single evaluate call
    page.evaluate("""
        () => {
            localStorage.setItem("session", 'xxxxxx');
            localStorage.setItem("groupIbServerSession", 'xxxxx');
            localStorage.setItem("awswaf_token_refresh_timestamp", 'xxxxxx');
        }
    """) # These are example data, and should be changed by your actual session tokens from your browser sessions

    # 3. Reload to let the web app recognize the injected session
    page.goto("https://www.betsson.es/casino/tragaperras-slots/bubble-up?gameAction=play")

    return page, context

def get_credit_and_bet():
    with open("credit.png", "rb") as file:
        response = requests.post(
            api_url,
            files={"filename": file},
            data={
                "apikey": api_key,
                "language": "spa",
                "isOverlayRequired": False,
                "OCREngine": 2,
            },
        )

    result = response.json()
    credit = 0
    bet = 0
    if not result.get("IsErroredOnProcessing"):
        parsed_text = result["ParsedResults"][0]["ParsedText"]
        numbers = re.findall(r"\d+(?:,\d+)?", parsed_text)
        print(numbers)
        credit = float(numbers[0].replace(",", "."))
        bet = float(numbers[1].replace(",", "."))
        print(credit)
        print(bet)
        print("Extracted Text:\n", parsed_text)
        return credit, bet
    else:
        print("Error:", result.get("ErrorMessage"))
        return 0, 0

if __name__ == "__main__":
    with sync_playwright() as p:
        page, context = setup_browser(p)
        
        print("Session injected. Check browser window...")
        time.sleep(20)
        viewport = page.viewport_size
        width = viewport["width"]
        height = viewport["height"]
        page.screenshot(path="browser.png")
        page.screenshot(path="credit.png", clip={"x":width*.17, "y": height*.73, "width": width*0.1, "height": height*.1})
        

        api_url = os.getenv("OCR_API_URL")
        api_key = os.getenv("OCR_API_KEY")

        credit, bet = get_credit_and_bet()

        win_happened = False

        while not win_happened:

            page.mouse.click(x=700, y=562)
            time.sleep(5)
            
            page.screenshot(path="winnings.png", clip={"x": width*.3, "y": height*.73, "width": width*0.2, "height": height*.1})
            with open("winnings.png", "rb") as file:
                response = requests.post(
                    api_url,
                    files={"filename": file},
                    data={
                        "apikey": api_key,
                        "language": "spa",  # Language code (e.g., 'eng', 'spa', 'fre')
                        "isOverlayRequired": False,
                        "OCREngine": 2,     # Engine 1 or 2 (Engine 2 works better for numbers/digits)
                    },
                )

            result = response.json()
            if not result.get("IsErroredOnProcessing"):
                parsed_text = result["ParsedResults"][0]["ParsedText"]
                print("Extracted Text:\n", parsed_text)
                if "HAGA" in parsed_text:
                    expected_credit = round(credit-bet, 2)
                    page.screenshot(path="browser.png")
                    page.screenshot(path="credit.png", clip={"x":width*.17, "y": height*.73, "width": width*0.1, "height": height*.1})
                    actual_credit, _ = get_credit_and_bet()
                    credit = actual_credit
                    if expected_credit == actual_credit:
                        print("[+] LOSS RECORDED CORRECTLY.")
                    else:
                        print("[-] LOSS FAILED.")
                        print(str(expected_credit) + "vs. " + str(actual_credit))
                else:
                    time.sleep(5)
                    numbers = re.findall(r"\d+(?:,\d+)?", parsed_text)
                    winning = float(numbers[0].replace(",", "."))
                    expected_credit = round(credit-bet+winning, 2)
                    page.screenshot(path="browser.png")
                    page.screenshot(path="credit.png", clip={"x":width*.17, "y": height*.73, "width": width*0.1, "height": height*.1})
                    actual_credit, _ = get_credit_and_bet()
                    win_happened = True
                    if expected_credit == actual_credit:
                        print("[+] WINNING RECORDED CORRECTLY.")
                    else:
                        print("[-] WINNING FAILED.")
                        print(str(expected_credit) + "vs. " + str(actual_credit))
            else:
                print("Error:", result.get("ErrorMessage"))

        input("Press Enter to exit and close browser...")
        
        context.close()
