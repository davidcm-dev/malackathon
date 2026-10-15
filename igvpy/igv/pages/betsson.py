"""Betsson's own site (not the provider game): DOM access is fine here. Selectors live in config/markets.py."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

from playwright.sync_api import Page

from config.markets import Market
from igv.vision.money import detect_currency, parse_amount


@dataclass
class Wallet:
    amount: float
    currency: str | None
    raw: str


class BetssonSite:
    def __init__(self, page: Page, market: Market):
        self.page, self.m = page, market

    def open(self) -> None:
        self.page.goto(self.m.lobby_url, wait_until="domcontentloaded")
        self.accept_cookies()
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

    def accept_cookies(self) -> None:
        btn = self.page.get_by_role("button", name=re.compile(r"accept all|allow all|accept|aceptar todo|aceptar", re.I)).first
        try:
            if btn.is_visible(timeout=5000):
                btn.click()
        except Exception:
            pass

    def login(self, user: str, password: str) -> None:
        self.page.get_by_role("button", name=self.m.login_button).first.click()
        self.page.locator('input[type="email"], input[name*="user" i], input[id*="user" i], input[name*="email" i]').first.fill(user)
        self.page.locator('input[type="password"]').first.fill(password)
        self.page.keyboard.press("Enter")
        if not self.wait_for_wallet(45):
            raise RuntimeError("Login did not complete: Betsson balance never appeared")

    def wallet(self) -> Wallet | None:
        for sel in self.m.balance_selectors:
            loc = self.page.locator(sel).first
            try:
                if loc.is_visible():
                    raw = loc.inner_text().strip()
                    amt = parse_amount(raw)
                    if amt is not None:
                        return Wallet(amt, detect_currency(raw), raw)
            except Exception:
                continue
        try:
            header = self.page.locator("header").first.inner_text()
        except Exception:
            header = ""
        r = re.search(r"(?:€|S\s?/\.?)\s?\d[\d.,]*|\d[\d.,]*\s?(?:€|EUR|PEN)", header)
        return Wallet(parse_amount(r.group(0)), detect_currency(r.group(0)), r.group(0)) if r else None

    def wait_for_wallet(self, timeout_s: float = 20) -> Wallet | None:
        for _ in range(int(timeout_s)):
            w = self.wallet()
            if w:
                return w
            self.page.wait_for_timeout(1000)
        return None

    def wallet_after_game(self) -> Wallet | None:
        """Betsson balance as the player sees it; if the game page hides the header, go back to the lobby."""
        w = self.wallet()
        if w:
            return w
        self.page.goto(self.m.lobby_url, wait_until="domcontentloaded")
        return self.wait_for_wallet(20)

    def launch_game(self) -> None:
        direct = os.getenv(f"GAME_URL_{self.m.env_prefix}")
        if direct:
            self.page.goto(direct, wait_until="domcontentloaded")
        else:
            name = os.getenv("GAME_NAME", "Sweet Bonanza")
            search = self.page.get_by_role("searchbox").or_(self.page.get_by_placeholder(re.compile(r"search|buscar", re.I))).first
            try:
                visible = search.is_visible(timeout=3000)
            except Exception:
                visible = False
            if not visible:
                self.page.get_by_role("button", name=re.compile(r"search|buscar", re.I)).first.click()
            search.fill(name)
            self.page.get_by_role("link", name=re.compile(name, re.I)).first.click()
        # Real Play only (never demo / fun mode)
        real = self.page.get_by_role("button", name=self.m.real_play_button).or_(
            self.page.get_by_role("link", name=self.m.real_play_button)).first
        try:
            if real.is_visible(timeout=8000):
                real.click()
        except Exception:
            pass
