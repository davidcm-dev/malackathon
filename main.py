from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        extra_http_headers={
            "x-obg-trusted-traffic": "1",
            "x-obg-country-code": "ES",
            "x-obg-origin": "ES",
            "x-obg-internal": "1",
        }
    )
    page = context.new_page()
    page.goto("https://www.betsson.es")

    button = page.get_by_role("button", name="Iniciar sesión")
    button.wait_for()
    button.click()

    email = page.get_by_label("Email")
    email.wait_for()
    email.press_sequentially("leopold202610159333938pg425scpvu@betssongroup.com")

    pwd = page.get_by_label("Contraseña")
    pwd.press_sequentially("SmokeTest123")

    page.get_by_role("button", name="Iniciar sesión").last.click()

    input("Press Enter to close...")
    context.close()