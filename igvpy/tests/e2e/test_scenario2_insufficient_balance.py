import re

import pytest

from igv.pages.betsson import BetssonSite
from igv.pages.pragmatic import PragmaticGame
from igv.vision.money import detect_currency, fmt, near
from igv.vision.ocr import ocr_text

pytestmark = [pytest.mark.scenario("S2 Insufficient balance"), pytest.mark.account("lowbal")]


def test_insufficient_balance(player, market, checks, evidence):
    page, site = player, BetssonSite(player, market)

    site.open()
    wallet_before = site.wait_for_wallet(30)
    checks.check("Authenticated: Betsson balance visible", wallet_before is not None, wallet_before.raw if wallet_before else "no balance found")
    if not wallet_before:
        return checks.assert_all()

    site.launch_game()
    game = PragmaticGame(page, market)
    before = game.wait_ready()
    evidence.snap("game-before-attempt", game.shot())
    checks.check(f"Currency is {market.currency_code}",
                 wallet_before.currency == market.currency_code and before.currency == market.currency_code,
                 f"betsson={wallet_before.currency} game={before.currency}")
    checks.check("Account really cannot afford the wager",
                 before.balance is not None and before.bet is not None and before.balance < before.bet,
                 f"balance={fmt(before.balance)} bet={fmt(before.bet)}")

    # attempt the spin, then read what the player actually sees
    game.spin()
    message, shown = "", False
    for _ in range(8):
        page.wait_for_timeout(1500)
        img = game.shot()
        for invert in (False, True):
            t = re.sub(r"\s+", " ", ocr_text(img, scale=1.5, invert=invert, sparse=True))
            if market.insufficient.search(t):
                message, shown = t, True
                evidence.snap("insufficient-message", img)
                break
        if shown:
            break
    checks.check("Insufficient-balance message visible on screen", shown, "message found by OCR" if shown else "no matching message within 12 s")
    checks.check(f"Message is in the expected language ({market.language})", shown and not market.wrong_language.search(message), message[:120])
    if message:
        checks.info("Message currency", detect_currency(message) or "none shown")

    # nothing was charged
    after = game.hud()
    evidence.snap("game-after-attempt", game.shot())
    checks.check("Spin rejected: in-game balance unchanged", near(after.balance, before.balance), f"before={fmt(before.balance)} after={fmt(after.balance)}")
    checks.check("No paid spin: no win shown", not after.win, f"win={fmt(after.win)}")
    page.wait_for_timeout(3000)
    wallet_after = site.wallet_after_game()
    evidence.snap("betsson-balance-after", page.screenshot())
    checks.check("Betsson balance unchanged", wallet_after is not None and near(wallet_after.amount, wallet_before.amount),
                 f"before={fmt(wallet_before.amount)} after={fmt(wallet_after.amount if wallet_after else None)}")
    checks.check(f"Currency still {market.currency_code}", wallet_after is not None and wallet_after.currency == market.currency_code,
                 f"read {wallet_after.currency if wallet_after else None}")
    checks.assert_all()
