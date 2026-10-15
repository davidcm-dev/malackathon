# Intelligent Game Validation (Malackathon 2026 · Betsson) - Python

Tests a Pragmatic Play game inside Betsson **the way a player sees it**. The game (iframe + canvas) is a
black box: we only take pixels of its canvas and send mouse/keyboard input. Every verdict comes from the screen.

## How it "sees like a player"
| Need | Technique |
|---|---|
| Read balance / wager / win / currency | OCR (pytesseract, `eng+spa`) on the HUD strip of the canvas (`igv/vision/hud.py`) |
| Did the spin start and finish? | Pixel difference of the reel area: idle noise floor → sustained motion (started) → still period (settled) (`igv/vision/motion.py`) |
| Insufficient-balance message + language | OCR of the whole canvas, matched against per-market regex; the wrong-language regex must NOT match |
| Betsson wallet balance | Betsson's own header (DOM allowed there), polled to absorb wallet lag |
| Balance rule | `after = before − wager + payout`, checked in-game **and** in Betsson; implied wager must equal the displayed wager |

A click is never a pass: "started" needs visible motion, "completed" needs the screen to settle, and money is reconciled with numbers read from the screen.

## Layout
```
config/markets.py              per-market URL, locale, currency, language, HUD labels, messages
igv/vision/                    ocr, hud parsing, motion detection, money parsing
igv/pages/betsson.py           lobby, login, wallet, game launch
igv/pages/pragmatic.py         canvas screenshots, spin input, settled HUD
igv/report.py                  pass/fail log per scenario+market, screenshot evidence
conftest.py                    --market option, browser, login (no recording), video per test
tests/unit/                    parsing tests (no browser)
tests/e2e/                     scenario 1 and scenario 2
scripts/summary.py             merged report: pass/fail table + screenshots + video
.github/workflows/validate.yml matrix per market, evidence artifact, GitHub Pages
```

## Run locally
```bash
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-spa   # macOS: brew install tesseract tesseract-lang
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && playwright install chromium
cp .env.example .env     # fill in the supplied test users
pytest tests/unit
pytest tests/e2e --market betsson-com      # or betsson-pe
HEADED=1 pytest tests/e2e --market betsson-pe -s
python scripts/summary.py                  # -> site/index.html
```

## Secrets
Credentials only via env vars / GitHub Secrets (names in `.env.example`). Login runs in a context with video and
trace off, so credentials never reach screenshots or recordings; the session is kept in `.auth/` (git-ignored, not uploaded).
GitHub setup: add the secrets from `.env.example`; Settings → Pages → Source = GitHub Actions.

## Calibrate on site (first hour, with the mentors)
Written without access to the live sites, so confirm:
1. `config/markets.py`: login button, real-play button, wallet selectors.
2. Game launch: set `GAME_NAME` or `GAME_URL_BETSSON_COM` / `_PE`.
3. HUD parsing: check `*-game-before-spin.png`; if balance/bet are not read, adjust the labels or the strip height in `hud.py` (default: bottom 18%).
4. Spin input: default is the Space key; if the game ignores it set `SPIN_BUTTON_XY="0.80,0.82"`.

## Known limits
- Free-spin / bonus rounds break the simple balance rule; the run is reported, not silently passed.
- betsson.pe may geo-block GitHub runners: use `BETSSON_PE_PROXY` or a self-hosted runner in the region.
- Session reuse relies on `storage_state`; if the session also needs sessionStorage, log in inside the test instead.
# malackathon
