from playwright.sync_api import expect, sync_playwright
from dotenv import load_dotenv
import os
import time
import re

load_dotenv()

def setup_browser(p):
    browser = p.chromium.launch(headless=False, executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    context = browser.new_context(
        extra_http_headers={
            "x-obg-trusted-traffic": "1",
            "x-obg-country-code": "ES",
            "x-obg-origin": "ES",
            "x-obg-internal": "1",
        }
    )

    page = context.new_page()
    page.goto("https://www.betsson.es/casino/tragaperras-slots/bubble-up?gameAction=play")

    page.evaluate("""
    () => {
        localStorage.setItem("session", '{"token":"ewogICJhbGciOiAiSFMyNTYiLAogICJ0eXAiOiAiSldUIgp9.ewogICJjcmVhdGVkQXQiOiAiMjAyNi0xMC0xNVQxMzoxMTowOS45NzA4NDU4WiIsCiAgInVzZXJJZCI6ICI5MTJhZmIzNS1jZTZjLTRlOGMtOWY5Ni0xMzA2NmVlYzcwYzMiLAogICJsb2dpblNlc3Npb25JZCI6ICI1OThkN2E1Zi05YzEwLTRiZGQtYmIyNi00MjRhMTAyMjhkZjAiLAogICJqdXJpc2RpY3Rpb24iOiAiRGdvaiIKfQ.mfo-SK_s767tj3II0WbaHbcxS5fGDDgB-Dy6_LrqYfE","timeToLiveSeconds":1199.5282123,"isFirstLogin":false,"startTimestamp":1792069869439,"customerId":"912afb35-ce6c-4e8c-9f96-13066eec70c3","jurisdiction":"Dgoj","startReason":"Login","lastLoginDate":"2026-10-15T13:00:28.403Z"}');
    }
    """)
    # page.evaluate("""
    #     () => {
    #         localStorage.setItem("session-token-expiration", '1792070301089.8318');
    #     }
    # """)
    # page.evaluate("""
    #     () => {
    #         localStorage.setItem("authSession", '{"timeToLiveSeconds":1199.4938317,"customerId":"912afb35-ce6c-4e8c-9f96-13066eec70c3","jurisdiction":"Dgoj","isFirstLogin":false,"sessionToken":"ewogICJhbGciOiAiSFMyNTYiLAogICJ0eXAiOiAiSldUIgp9.ewogICJjcmVhdGVkQXQiOiAiMjAyNi0xMC0xNVQxMjo1ODoyMS43NDgzNTYyWiIsCiAgInVzZXJJZCI6ICI5MTJhZmIzNS1jZTZjLTRlOGMtOWY5Ni0xMzA2NmVlYzcwYzMiLAogICJsb2dpblNlc3Npb25JZCI6ICJjNDNlNWI4Ny03NmNhLTRjYzAtODJkMi0zYjA5ZTI2OTkyODYiLAogICJqdXJpc2RpY3Rpb24iOiAiRGdvaiIKfQ.x5ubn4r0x7-FWYSupxVI7uMkLDJtpR2BG32cxLEvswU"}');
    #     }
    # """)
    page.evaluate("""
        () => {
            localStorage.setItem("groupIbServerSession", '{"token":"3952f2f9-cf71-4de7-940f-8bd48a9561d4","type":"authenticated","expiry":"2026-10-15T13:07:33.602Z"}');
        }
    """)
    # page.evaluate("""
    #     () => {
    #         localStorage.setItem("gaming-session-check", '{"sessionStartTime":"2026-10-15T12:58:28.614Z","nextRealityCheck":"2026-10-15T13:58:28.614Z","nextSnackbar":"2026-10-15T13:13:28.614Z"}');
    #     }
    # """)
    page.evaluate("""
        () => {
            localStorage.setItem("awswaf_token_refresh_timestamp", '1792070644511');
        }
    """)

    # page.goto("https://www.betsson.es/api/v1/Gamelauncher/?gameId=pragmaticPlayBubbleUp&brandId=ff28e5bd-a193-4f34-9abe-af70ffbd1dbf&marketCode=es&forReal=true&host=https%3A%2F%2Fwww.betsson.es&depositUrl=deposit&accountHistoryUrl=transaction-history&x-obg-device=Desktop&x-obg-channel=Web&x-obg-country-code=ES&primaryVariantId=pragmaticPlayBubbleUp&provider=PragmaticPlay&primaryType=Slots&sessionToken=ewogICJhbGciOiAiSFMyNTYiLAogICJ0eXAiOiAiSldUIgp9.ewogICJjcmVhdGVkQXQiOiAiMjAyNi0xMC0xNVQxMzoxMTowOS45NzA4NDU4WiIsCiAgInVzZXJJZCI6ICI5MTJhZmIzNS1jZTZjLTRlOGMtOWY5Ni0xMzA2NmVlYzcwYzMiLAogICJsb2dpblNlc3Npb25JZCI6ICI1OThkN2E1Zi05YzEwLTRiZGQtYmIyNi00MjRhMTAyMjhkZjAiLAogICJqdXJpc2RpY3Rpb24iOiAiRGdvaiIKfQ.mfo-SK_s767tj3II0WbaHbcxS5fGDDgB-Dy6_LrqYfE")

    page.reload()

    # expect(page).to_have_url(re.compile(r"^https://www\.betsson\.es(?:/|$)"))
    return page, context

# def click_login_button(page):
#     button = page.get_by_role("button", name="Iniciar sesión")
#     button.wait_for()
#     button.click()

# def type_email_and_password(page):
#     email = page.get_by_label("Email")
#     email.wait_for()
#     email.press_sequentially(os.getenv("FUNDED_EMAIL"), delay=80)

#     pwd = page.get_by_label("Contraseña")
#     pwd.press_sequentially(os.getenv("PASSWORD"), delay=80)

# def send_login(page):
#     page.get_by_role("button", name="Iniciar sesión").last.click()

with sync_playwright() as p:
    page, context = setup_browser(p)
    time.sleep(5)
    # click_login_button(page)
    # type_email_and_password(page)
    # send_login(page)
    # page.goto("https://www.betsson.es/casino/tragaperras-slots/bubble-up?gameAction=play")
    input("Press any key to exit...")
    context.close()