from PIL import Image
import pytesseract


def ocr():
    return pytesseract.image_to_string(Image.open("card.webp"))
