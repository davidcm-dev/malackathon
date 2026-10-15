import re


def parse_amount(raw: str | None) -> float | None:
    """'€1,000.50', 'S/ 1.000,50', '0.20' -> float."""
    if not raw:
        return None
    m = re.sub(r"[^\d.,]", "", raw)
    m = re.sub(r"^[.,]+|[.,]+$", "", m)
    if not re.search(r"\d", m):
        return None
    sep = max(m.rfind("."), m.rfind(","))
    int_part, frac = m, ""
    if sep >= 0 and len(m) - sep - 1 <= 2:
        int_part, frac = m[:sep], m[sep + 1:]
    int_part = re.sub(r"[.,]", "", int_part) or "0"
    return float(f"{int_part}.{frac}" if frac else int_part)


def detect_currency(raw: str | None) -> str | None:
    if not raw:
        return None
    if re.search(r"€|\bEUR\b", raw, re.I):
        return "EUR"
    if re.search(r"S\s?/\.?|\bPEN\b|sol", raw, re.I):
        return "PEN"
    return None


def near(a: float | None, b: float | None, tol: float = 0.005) -> bool:
    return a is not None and b is not None and abs(a - b) <= tol


def fmt(n: float | None) -> str:
    return "n/a" if n is None else f"{n:.2f}"
