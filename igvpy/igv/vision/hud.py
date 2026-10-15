from __future__ import annotations

import io
import re
from dataclasses import dataclass

from config.markets import Market
from .money import detect_currency, parse_amount

AMT = r"((?:€|S\s?/\.?|EUR|PEN)?\s?\d[\d.,]*)"


@dataclass
class Hud:
    balance: float | None = None
    bet: float | None = None
    win: float | None = None      # None = no WIN figure visible on screen
    currency: str | None = None
    text: str = ""


def parse_hud(text: str, m: Market) -> Hud:
    def grab(labels: str) -> str | None:
        r = re.search(rf"(?:{labels})[\s:]{{0,3}}{AMT}", text, re.I)
        return r.group(1).strip() if r else None

    bal, bet, win = grab(m.label_balance), grab(m.label_bet), grab(m.label_win)
    return Hud(
        balance=parse_amount(bal),
        bet=parse_amount(bet),
        win=None if win is None else parse_amount(win),
        currency=detect_currency(bal) or detect_currency(bet) or detect_currency(win),
        text=text,
    )


def read_hud(img: bytes, m: Market) -> Hud:
    """Read balance / bet / win / currency from the bottom HUD strip of a game screenshot."""
    from PIL import Image
    from .ocr import ocr_text

    w, h = Image.open(io.BytesIO(img)).size
    crop = (0, int(h * 0.82), w, h)
    best = Hud()
    score = lambda x: int(x.balance is not None) + int(x.bet is not None)
    for invert in (True, False):
        text = re.sub(r"\s+", " ", ocr_text(img, crop=crop, scale=3, invert=invert, sparse=True))
        hud = parse_hud(text, m)
        if hud.balance is not None and hud.bet is not None:
            return hud
        if score(hud) > score(best):
            best = hud
    return best
