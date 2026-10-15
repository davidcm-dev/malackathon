import pytest

from igv.pages.betsson import BetssonSite
from igv.pages.pragmatic import PragmaticGame
from igv.vision.money import fmt, near
from igv.vision.motion import observe_spin

pytestmark = [pytest.mark.scenario("S1 Completed spin"), pytest.mark.account("funded")]


def test_completed_real_play_spin(player, market, checks, evidence):
    page, site = player, BetssonSite(player, market)

    # 1-2. lobby + authenticated session
    site.open()
    wallet_before = site.wait_for_wallet(30)
    evidence.snap("lobby-logged-in", page.screenshot())
    checks.check("Authenticated: Betsson balance visible", wallet_before is not None, wallet_before.raw if wallet_before else "no balance found")
    if not wallet_before:
        return checks.assert_all()
    checks.check(f"Betsson currency is {market.currency_code}", wallet_before.currency == market.currency_code, f"read {wallet_before.currency}")

    # 3-4. Pragmatic Play game in Real Play; read balance, wager, currency from pixels
    site.launch_game()
    game = PragmaticGame(page, market)
    before = game.wait_ready()
    evidence.snap("game-before-spin", game.shot())
    checks.check("Game HUD readable (balance, wager)", before.balance is not None and before.bet is not None, f"balance={fmt(before.balance)} bet={fmt(before.bet)}")
    checks.check(f"In-game currency is {market.currency_code}", before.currency == market.currency_code, f"read {before.currency}")
    checks.check("In-game balance equals Betsson balance before spin", near(before.balance, wallet_before.amount), f"game={fmt(before.balance)} betsson={fmt(wallet_before.amount)}")
    wager = before.bet

    # 5-6. spin and watch pixels: motion = game reacted, stillness = spin completed
    obs = observe_spin(game.shot, game.spin)
    if obs.started_frame:
        evidence.snap("spin-in-progress", obs.started_frame)
    checks.check("Spin started (reels visibly moved)", obs.started, f"peak motion={obs.peak_motion:.3f} noise={obs.noise_floor:.3f}")
    checks.check("Spin completed (reels settled)", obs.settled, f"{obs.duration_ms} ms")

    # 7. settled outcome + balances
    after = game.settled_hud()
    evidence.snap("game-after-spin", game.shot())
    payout = after.win or 0.0
    checks.info("Observed outcome", f"win={fmt(after.win)} ({'read from screen' if after.win is not None else 'no WIN figure on screen = 0'})")
    checks.check("Displayed wager unchanged after spin", near(after.bet, wager), f"before={fmt(wager)} after={fmt(after.bet)}")
    checks.check(f"In-game currency still {market.currency_code}", after.currency == market.currency_code, f"read {after.currency}")
    expected_game = (before.balance or 0) - (wager or 0) + payout
    checks.check("In-game balance = before - wager + payout", near(after.balance, expected_game), f"expected {fmt(expected_game)}, read {fmt(after.balance)}")
    if after.balance is not None:
        used = before.balance - after.balance + payout
        checks.check("Wager used for the spin equals displayed wager", near(used, wager), f"implied={fmt(used)} displayed={fmt(wager)}")

    # Betsson wallet reconciliation (wallet may lag the game: poll up to 20 s)
    expected = wallet_before.amount - (wager or 0) + payout
    wallet_after = site.wallet_after_game()
    for _ in range(10):
        if wallet_after and near(wallet_after.amount, expected):
            break
        page.wait_for_timeout(2000)
        wallet_after = site.wallet()
    evidence.snap("betsson-balance-after", page.screenshot())
    checks.check("Betsson balance = before - wager + payout", wallet_after is not None and near(wallet_after.amount, expected),
                 f"expected {fmt(expected)}, read {fmt(wallet_after.amount if wallet_after else None)}")
    checks.assert_all()
