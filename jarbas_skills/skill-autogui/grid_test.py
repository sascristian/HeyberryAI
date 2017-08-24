from os.path import dirname
import pyautogui
from PIL import ImageDraw, ImageFont, Image


def get_grid(path=None):
    if path is None:
        path = dirname(__file__) + "/screenshot.jpg"
    img = pyautogui.screenshot(path)
    #img = cv2.imread(path)
    w, h = img.size
    x = w / 3
    y = h / 3
    draw = ImageDraw.Draw(img)
    # draw vertical lines
    i = 0
    while i < 4:
        draw.line(((x * i, 0), (x * i, h)), fill=(255, 0, 0), width=5)
        #cv2.line(img, (x*i, 0), (x*i, h), (0, 0, 255), 5)
        i += 1
    # draw horizontal lines
    i = 0
    while i < 4:
        draw.line(((0, y*i), (w, y*i)), fill=(255, 0, 0), width=3)
        #cv2.line(img, (0, y*i), (w, y*i), (0, 0, 255), 5)
        i += 1
    # save num coordinates
    boundings = []
    num = 0
    for o in range(0, 3):
        for i in range(0, 3):
            num += 1
            box = [x * i, o*y, x, y]
            print num, box
            boundings.append(box)

    # draw nums
    for num in range(1, 10):
        box = boundings[num-1]
        x = box[2] / 2 + box[0]
        y = box[3] / 2 + box[1]
        font = ImageFont.truetype(dirname(__file__) + "/METALORD.TTF", 30)
        draw.text((x, y), str(num), (255, 0, 0), font)

    img.save(path)
    return path

print get_grid()[0]
