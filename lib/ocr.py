# all of this code was taken from https://github.com/riccardolunardi/KarutaBotHack

try:
    from PIL import Image
except ImportError:
    import Image

from os import listdir
from os.path import isfile, join

import cv2
import pytesseract
import requests


async def download(url):
    filename = "main.png"

    with open(filename, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

    return filename


def filelength(filepath):
    im = cv2.imread(filepath)
    return im.shape[1]


def change_contrast(img0, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img0.point(contrast)


async def get_card(path, input0, n_img):
    img0 = cv2.imread(input0)
    crop_img = img0[0: 0 + 414, n_img * 278: n_img * 278 + 278]
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path, crop_img)


async def get_top(input0, output):
    img0 = cv2.imread(input0)
    crop_img = img0[65:105, 45:230]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(output, gray)


async def get_bottom(input0, output):
    img = cv2.imread(input0)
    crop_img = img[55 + 255 : 110 + 255, 45:235]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(output, gray)


async def get_print(input0, output):
    img0 = cv2.imread(input0)
    crop_img = img0[372:385, 145:203]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(output, gray)


# TESTS
if __name__ == "__main__":
    fname = download(
        "https://media.discordapp.net/attachments/776520559621570621/974137396184641546/card.webp"
    )
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
    custom_config = r"--psm 10 --oem 3 -c " \
                    r"tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:!'\"," \
                    r".@&#0123456789() "
    for img in onlyfiles:
        print(
            pytesseract.image_to_string(
                Image.open(path_to_ocr + "/" + img), lang="eng", config="--psm 6"
            ).strip()
        )
