"""Pragmatic Play game treated as a black box: canvas pixels in, mouse/keyboard out. No game DOM is read."""
from __future__ import annotations

import os
import time

from playwright.sync_api import Locator, Page

from config.markets import Market
from igv.vision.hud import Hud, read_hud


class PragmaticGame:
    def __init__(self, page: Page, market: Market):
        self.page, self.m = page, market
        self.canvas: Locator | None = None

    def locate_canvas(self, timeout_s: float = 90) -> None:
        end = time.time() + timeout_s
        while time.time() < end:
            best, best_area = None, 0
            for fr in self.page.frames:
                loc = fr.locator("canvas")
                try:
                    n = loc.count()
                except Exception:
                    continue
                for i in range(n):
                    c = loc.nth(i)
                    try:
                        b = c.bounding_box()
                    except Exception:
                        b = None
                    if b and b["width"] > 400 and b["height"] > 250 and b["width"] * b["height"] > best_area:
                        best, best_area = c, b["width"] * b["height"]
            if best:
                self.canvas = best
                return
            self.page.wait_for_timeout(1000)
        raise RuntimeError("Game canvas not found (game did not render)")

    def shot(self) -> bytes:
        return self.canvas.screenshot(type="png")

    def hud(self) -> Hud:
        return read_hud(self.shot(), self.m)

    def wait_ready(self, timeout_s: float = 120) -> Hud:
        """Wait until the HUD is readable; click a neutral spot to get past 'tap to continue' intros."""
        self.locate_canvas()
        end = time.time() + timeout_s
        while time.time() < end:
            h = self.hud()
            if h.balance is not None and h.bet is not None:
                return h
            b = self.canvas.bounding_box()
            if b:
                self.page.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] * 0.35)
            self.page.wait_for_timeout(3000)
        raise RuntimeError("Game HUD (balance / bet) never became readable on screen")

    def spin(self) -> None:
        b = self.canvas.bounding_box()
        xy = os.getenv("SPIN_BUTTON_XY")
        if xy:
            x, y = (float(v) for v in xy.split(","))
            self.page.mouse.click(b["x"] + b["width"] * x, b["y"] + b["height"] * y)
        else:  # focus via neutral margin click, then the provider's keyboard shortcut
            self.page.mouse.click(b["x"] + b["width"] * 0.02, b["y"] + b["height"] * 0.5)
            self.page.keyboard.press("Space")

    def settled_hud(self, timeout_s: float = 30) -> Hud:
        """Poll until balance and win stop changing (win count-up finished)."""
        end, last = time.time() + timeout_s, self.hud()
        while time.time() < end:
            self.page.wait_for_timeout(1500)
            h = self.hud()
            if h.balance is not None and h.balance == last.balance and h.win == last.win:
                return h
            last = h
        return last
