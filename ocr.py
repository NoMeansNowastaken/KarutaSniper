try:
    from PIL import Image
except ImportError:
    import Image

from os import listdir
from os.path import isfile, join

import cv2
import pytesseract
import requests


def download(url):
    filename = "main.png"

    with open(filename, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

    return filename


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


def get_card(path, input, n_img):
    img = cv2.imread(input)
    crop_img = img[0:0 + 414, n_img * 278:n_img * 278 + 278]
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path, crop_img)


def get_top(input, output):
    img = cv2.imread(input)
    crop_img = img[65:105, 45:230]
    # Grayscale, Gaussian blur, Otsu's threshold
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening
    cv2.imwrite(output, invert)


def get_bottom(input, output):
    img = cv2.imread(input)
    crop_img = img[55 + 255:110 + 255, 45:230]
    # Grayscale, Gaussian blur, Otsu's threshold
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening
    cv2.imwrite(output, invert)


# TESTS
if __name__ == "__main__":
    fname = download("https://media.discordapp.net/attachments/776520559621570621/974137396184641546/card.webp")
    path_to_ocr = "C:\\users\\user\\Desktop\\KarutaBotHack-main\\tests"
    for i in range(0, 3):
        get_card(f"card{i + 1}.png", fname, i)
        get_card(f"card{i + 1}.png", fname, i)
        get_card(f"card{i + 1}.png", fname, i)

    for i in range(0, 3):
        get_top(f"card{i + 1}.png", f"{path_to_ocr}/top{i + 1}.png")
        get_bottom(f"card{i + 1}.png", f"{path_to_ocr}/bottom{i + 1}.png")

    onlyfiles = [f for f in listdir(path_to_ocr) if isfile(join(path_to_ocr, f))]
    print("File trovati: ", onlyfiles)
    custom_config = r"--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:!'\",.@&#0123456789()"
    for img in onlyfiles:
        print(pytesseract.image_to_string(Image.open(path_to_ocr + "/" + img), lang='eng', config='--psm 6').strip())