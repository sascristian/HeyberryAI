from os.path import dirname
import pyautogui
import cv2
import PIL

def get_grid(path=None):
    if path is None:
        path = dirname(__file__) + "/screenshot.jpg"
    pyautogui.screenshot(path)
    img = cv2.imread(path)
    h, w = img.shape[:2]
    x = w / 3
    y = h / 3
    font = cv2.FONT_HERSHEY_SIMPLEX
    # draw vertical lines
    i = 0
    while i < 4:
        cv2.line(img, (x*i, 0), (x*i, h), (0, 0, 255), 5)

        i += 1
    # draw horizontal lines
    i = 0
    while i < 4:
        cv2.line(img, (0, y*i), (w, y*i), (0, 0, 255), 5)
        i += 1
    # save num coordinates
    self.boundings = []
    num = 0
    for o in range(0, 3):
        for i in range(0, 3):
            num += 1
            box = [x * i, o*y, x, y]
            print num, box
            self.boundings.append(box)

    # draw nums
    for num in range(1, 10):
        box = self.boundings[num-1]
        x = box[2] / 2 + box[0]
        y = box[3] / 2 + box[1]
        cv2.putText(img, str(num), (x, y), font,
                    1, (0, 0, 255), 2)

    cv2.imwrite(path, img)
    return path

print get_grid()
