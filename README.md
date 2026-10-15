# Slot Game Credit Checker

## About

This project is a Python script that automates a slot game in Firefox and checks if the credit balance changes correctly after each spin.

It uses Playwright to interact with the browser and OCR.space to read the numbers displayed on the screen. After each spin, it compares the actual credit balance with the expected one and prints the result.

## How it works

- Opens the game in Firefox.
- Takes screenshots of the credit, bet, and spin result.
- Uses OCR.space to extract the numbers from the screenshots.
- Calculates the expected credit balance after each spin.
- Compares the expected balance with the one displayed in the game.
- Prints whether the balance matches or not.

The script keeps playing until it detects a win.

## Requirements

- Python 3.10 or later
- Firefox
- Playwright
- Requests
- python-dotenv
- An OCR.space API key

## Setup

Clone the repository and move into the project folder:

```bash
git clone <repository-url>
cd <project-folder>
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

**Windows**
```bash
.venv\Scripts\activate
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install playwright requests python-dotenv
playwright install firefox
```

## Configuration

The script uses OCR.space to read text from screenshots. You need an API key to use this service.

Create a `.env` file in the project folder:

```env
OCR_API_KEY=your_api_key
OCR_API_URL=https://api.ocr.space/parse/image
```

Update the script to load these values from the environment instead of keeping the API key directly in the code.

The script also relies on browser session data to access the game. This session may expire, so you might need to update the authentication setup.

## Running the script

Run the Python file:

```bash
python main.py
```

Replace `main.py` with the actual filename if it is different.

The browser will open and the script will start reading the credit and bet values. It then clicks the spin button, checks the result, and compares the new credit balance with the expected value.

When a win is detected, the loop stops. Press Enter in the terminal to close the browser.

## Credit calculation

After a loss, the expected balance is calculated as:

```python
expected_credit = round(credit - bet, 2)
```

After a win:

```python
expected_credit = round(credit - bet + winning, 2)
```

The script compares this value with the credit balance extracted from the screenshot.

## Screenshots

The script saves three screenshots in the project folder:

- `browser.png` — the browser page.
- `credit.png` — the credit and bet values.
- `winnings.png` — the result of the spin.

These files are overwritten when new screenshots are taken.

Apart from that, you can see a screenshot called `2026-10-15-193222_hyprshot.png` that shows the console output on a run we performed. The system first detects a loss correctly and checks the final balance is correct, then does the same for a win.

## Known issues

- The mouse coordinates are fixed, so the script may not work with different screen sizes.
- It uses fixed delays, which may not be enough if the game loads slowly.
- OCR can misread numbers or fail to detect them.
- The script may keep running if it never detects a win.
- The browser session can expire.
- Network errors and unexpected game states are not fully handled.

## Notes

This is a small automation project for testing credit balance changes using browser automation and OCR. The results depend on the accuracy of the text recognition and the game interface.

Do not commit API keys or session tokens to the repository. If credentials have already been exposed, revoke or replace them before publishing the project.
