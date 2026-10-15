"""Per-market configuration. Nothing secret lives here: credentials come from env vars."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Market:
    id: str
    name: str
    base_url: str
    lobby_path: str
    locale: str
    timezone: str
    language: str                      # "en" | "es"
    geolocation: dict
    currency_code: str                 # "EUR" | "PEN"
    currency_pattern: re.Pattern
    env_prefix: str
    login_button: re.Pattern
    real_play_button: re.Pattern
    balance_selectors: tuple = field(default_factory=tuple)
    # regex alternations for the labels printed in the game HUD
    label_balance: str = ""
    label_bet: str = ""
    label_win: str = ""
    insufficient: re.Pattern = re.compile(r"$^")
    wrong_language: re.Pattern = re.compile(r"$^")

    @property
    def lobby_url(self) -> str:
        return self.base_url + self.lobby_path


I = re.I
MARKETS: dict[str, Market] = {
    "betsson-com": Market(
        id="betsson-com",
        name="betsson.com (English / EUR)",
        base_url=os.getenv("BETSSON_COM_URL", "https://www.betsson.com"),
        lobby_path="/en/casino",
        locale="en-GB",
        timezone="Europe/Madrid",
        language="en",
        geolocation={"latitude": 36.72, "longitude": -4.42},
        currency_code="EUR",
        currency_pattern=re.compile(r"€|\bEUR\b"),
        env_prefix="BETSSON_COM",
        login_button=re.compile(r"^\s*log\s?in\s*$", I),
        real_play_button=re.compile(r"play for real|real play|play now|^\s*play\s*$", I),
        balance_selectors=('[data-test-id*="balance" i]', '[class*="balance" i]', '[data-testid*="balance" i]'),
        label_balance="CREDIT|BALANCE",
        label_bet="BET|TOTAL BET",
        label_win="TOTAL WIN|LAST WIN|WIN",
        insufficient=re.compile(r"insufficient|not enough|low balance|funds|deposit", I),
        wrong_language=re.compile(r"saldo|fondos|insuficiente|apuesta", I),
    ),
    "betsson-pe": Market(
        id="betsson-pe",
        name="betsson.pe (Spanish / PEN)",
        base_url=os.getenv("BETSSON_PE_URL", "https://www.betsson.pe"),
        lobby_path="/casino",
        locale="es-PE",
        timezone="America/Lima",
        language="es",
        geolocation={"latitude": -12.05, "longitude": -77.04},
        currency_code="PEN",
        currency_pattern=re.compile(r"S\s?/\.?|\bPEN\b"),
        env_prefix="BETSSON_PE",
        login_button=re.compile(r"iniciar sesi[oó]n|ingresar|entrar|acceder", I),
        real_play_button=re.compile(r"jugar con dinero real|jugar real|jugar ahora|^\s*jugar\s*$", I),
        balance_selectors=('[data-test-id*="balance" i]', '[class*="balance" i]', '[class*="saldo" i]'),
        label_balance="SALDO|CR[EÉ]DITO|CREDIT|BALANCE",
        label_bet="APUESTA TOTAL|APUESTA|BET",
        label_win="GANANCIA|PREMIO|TOTAL WIN|WIN",
        insufficient=re.compile(
            r"saldo insuficiente|fondos insuficientes|insuficiente|no (?:tienes|dispones de) (?:suficiente|saldo)|saldo (?:bajo|no es suficiente)|dep[oó]sit",
            I,
        ),
        wrong_language=re.compile(r"insufficient|not enough|funds|balance too low", I),
    ),
}


def credentials(m: Market, kind: str) -> tuple[str | None, str | None]:
    p = m.env_prefix if kind == "funded" else f"{m.env_prefix}_LOWBAL"
    return os.getenv(f"{p}_USER"), os.getenv(f"{p}_PASS")


def auth_file(m: Market, kind: str) -> str:
    return f".auth/{m.id}-{kind}.json"
