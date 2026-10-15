from config.markets import MARKETS
from igv.vision.hud import parse_hud
from igv.vision.money import detect_currency, parse_amount


def test_parse_amount():
    assert parse_amount("€1,000.50") == 1000.50
    assert parse_amount("S/ 1.000,50") == 1000.50
    assert parse_amount("0.20") == 0.20
    assert parse_amount("S/. 5.00") == 5.0
    assert parse_amount("1,000") == 1000.0
    assert parse_amount("abc") is None


def test_currency():
    assert detect_currency("€10") == "EUR"
    assert detect_currency("S/ 10.00") == "PEN"


def test_hud_en():
    h = parse_hud("CREDIT €1,000.00 BET €0.20 WIN €1.50", MARKETS["betsson-com"])
    assert (h.balance, h.bet, h.win, h.currency) == (1000.0, 0.2, 1.5, "EUR")


def test_hud_es():
    h = parse_hud("SALDO S/ 100.00 APUESTA S/ 1.00", MARKETS["betsson-pe"])
    assert (h.balance, h.bet, h.win, h.currency) == (100.0, 1.0, None, "PEN")


def test_messages_language():
    en, es = MARKETS["betsson-com"], MARKETS["betsson-pe"]
    assert es.insufficient.search("Saldo insuficiente") and not es.wrong_language.search("Saldo insuficiente")
    assert en.insufficient.search("Insufficient funds") and not en.wrong_language.search("Insufficient funds")
    assert es.wrong_language.search("Insufficient funds")
