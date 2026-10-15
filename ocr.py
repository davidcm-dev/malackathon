import cv2
import pytesseract

SCREENSHOT = "screenshot.png"
SCREENSHOT2 = "screenshot2.png"
SUBIMAGE = "subimage.png"

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# 1. Detect text in your screenshot
image = cv2.imread(SCREENSHOT)

if image is None:
    raise FileNotFoundError(SCREENSHOT)

text = pytesseract.image_to_string(image)
print("Detected text:")
print(text)

# 2. Find your target PNG inside the screenshot
target = cv2.imread(SUBIMAGE)
image = cv2.imread(SCREENSHOT2)

if target is None:
    raise FileNotFoundError(SUBIMAGE)

result = cv2.matchTemplate(
    image, target, cv2.TM_CCOEFF_NORMED
)

_, score, _, location = cv2.minMaxLoc(result)

print("Image similarity:", round(score, 3))

if score >= 0.85:
    h, w = target.shape[:2]
    print("Image found at:", location)
    print("Center:", (location[0] + w // 2,
                       location[1] + h // 2))
else:
    print("Target image not found confidently.")
