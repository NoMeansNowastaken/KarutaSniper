# all of this code was taken from https://github.com/riccardolunardi/KarutaBotHack
try:
    from PIL import Image
except ImportError:
    import Image

import cv2


def filelength(filepath):
    im = cv2.imread(filepath)
    return im.shape[1]


async def get_card(path, input0, n_img):
    img0 = cv2.imread(input0)
    crop_img = img0[0: 0 + 414, n_img * 278: n_img * 278 + 278]
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path, crop_img)


async def tofu_get_card(path, input0, n_img):
    img0 = cv2.imread(input0)
    crop_img = img0[0:480, n_img * 313:313 + 313 * n_img]
    cv2.imwrite(path, crop_img)


async def get_top(input0, output):
    img0 = cv2.imread(input0)
    crop_img = img0[65:105, 45:230]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(output, gray)


async def tofu_get_top(input0, output):
    img0 = cv2.imread(input0)
    crop_img = img0[27:77, 54:259]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 4)
    cv2.imwrite(output, th)


async def get_bottom(input0, output):
    img = cv2.imread(input0)
    crop_img = img[55 + 255: 110 + 255, 45:235]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 4)
    cv2.imwrite(output, th)


async def tofu_get_bottom(input0, output):
    img = cv2.imread(input0)
    crop_img = img[400:452, 55:260]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    th, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_OTSU)
    cv2.imwrite(output, binary)


async def get_print(input0, output):
    img0 = cv2.imread(input0)
    crop_img = img0[372:385, 145:203]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(output, gray)


async def tofu_get_print(input0, output):
    img0 = cv2.imread(input0)
    crop_img = img0[362:387, 210:264]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    th, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_OTSU)
    cv2.imwrite(output, binary)
