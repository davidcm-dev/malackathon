"""OCR on pixels only (pytesseract). Needs the tesseract binary + eng/spa language data."""
from __future__ import annotations

import io


def ocr_text(img: bytes, crop: tuple[int, int, int, int] | None = None,
             scale: float = 1.0, invert: bool = False, sparse: bool = False) -> str:
    import pytesseract
    from PIL import Image, ImageOps

    im = Image.open(io.BytesIO(img)).convert("RGB")
    if crop:
        im = im.crop(crop)  # (left, top, right, bottom)
    im = ImageOps.autocontrast(im.convert("L"))
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    if invert:
        im = ImageOps.invert(im)
    return pytesseract.image_to_string(im, lang="eng+spa", config="--psm 11" if sparse else "--psm 6")
