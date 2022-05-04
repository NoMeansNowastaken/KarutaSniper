from PIL import Image
import pytesseract


def ocr():
    text = pytesseract.image_to_string(Image.open('card.webp'))
    return text
