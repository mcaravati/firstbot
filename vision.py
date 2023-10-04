import subprocess
import sys
import time


def install():
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )


# install()

import cv2
from skimage.morphology import skeletonize
import numpy as np
from matplotlib import pyplot as plt
import pypot

DEBUG = False
go = True

colors = {"black": [np.array([0, 0, 0]), np.array([180, 225, 80])]}
colors["green"] = [np.array([30, 50, 20]), np.array([65, 255, 255])]
colors["orange"] = [np.array([0, 20, 10]), np.array([20, 255, 255])]

detect = ["black", "green"]
d = 0
limit = "orange"
stamp = [time.time(), False]

cam_port = 0
cam = cv2.VideoCapture(cam_port)

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


def capture():
    _, img = cam.read()
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def compute(img):
    global go
    # img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    blur = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)
    hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lower_range = colors[detect[d]][0]
    upper_range = colors[detect[d]][1]
    mask = cv2.inRange(hsv_img, lower_range, upper_range)
    edged = cv2.Canny(mask, 30, 200)
    contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    skeleton = skeletonize(mask, method="lee")
    Y, X = np.where(skeleton > 0)
    xmoy = 120
    ymoy = 160

    try:
        xmoy = int(np.mean(X))
        ymoy = int(np.mean(Y))
    except:
        pass

    calc = (xmoy - 120) / 1.2

    if DEBUG :
        # render = cv2.add(img, skeleton)
        cv2.drawContours(img, contours, -1, (0, 255, 255), 1)
        cv2.drawMarker(img, (xmoy, ymoy), (0,0,255))
        cv2.imshow("rendering", img)

        if cv2.waitKey(1) == ord('q'):
            go = False
            cv2.destroyWindow("rendering")
            
    return calc


def swap(img):
    global d
    t = time.time()
    print("swap 0")
    if stamp[1] or (t - stamp[0] >= 5):
        print("swap 1")
        stamp[1] = True
        img[:300, :] = 0
        blur = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)
        hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        lower_range = colors[limit][0]
        upper_range = colors[limit][1]
        mask = cv2.inRange(hsv_img, lower_range, upper_range)
        Y,X = np.where(mask != 0)
        if len(Y) > 1500:
            d = (d + 1) % 2
            stamp[1] = False
            stamp[0] = t


if __name__ == "__main__":
    while go:
        image = capture()
        percent = compute(image)
        print(percent, detect[d])
        swap(image)
    cam.release()
