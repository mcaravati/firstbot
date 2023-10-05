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

#Colors limits
colors = {"black": [np.array([0, 0, 0]), np.array([180, 225, 60])]}
colors["green"] = [np.array([30, 50, 20]), np.array([65, 255, 255])]
colors["orange"] = [np.array([0, 20, 10]), np.array([20, 255, 255])]

#Witch color to detect
curr_col = 0
detect = ["black", "green"]
old_calc = 0
#Set swap color
limit = "orange"
stamp = [time.time(), False]

#Cam init
cam_port = 2
cam = cv2.VideoCapture(cam_port)
#Cam resolution
y_max = 160
x_max = 120
cam.set(cv2.CAP_PROP_FRAME_WIDTH, y_max)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, x_max)


#Capture image & return image to work with
def capture():
    _, img = cam.read()
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


#Line detection
def compute(img):
    global go, old_calc

    #remove imperfection with blur
    blur = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)
    #transform HSV
    hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    #set color range
    lower_range = colors[detect[curr_col]][0]
    upper_range = colors[detect[curr_col]][1]
    #masking
    mask = cv2.inRange(hsv_img, lower_range, upper_range)
    #generate mask's skeleton
    skeleton = skeletonize(mask, method="lee")

    #skeleton x,y mean
    Y, X = np.where(skeleton > 0)
    xmoy = x_max/2
    ymoy = y_max/2
    calc = old_calc
    try:
        xmoy = int(np.mean(X))
        ymoy = int(np.mean(Y))
        #normalize
        calc = max(min(((xmoy - (x_max/2)) / (x_max/200)), 80.0), -80.0)
    except:
        pass

    #video debug
    if DEBUG :
        
        edged = cv2.Canny(mask, 30, 200)
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(img, contours, -1, (0, 255, 255), 1)
        try:
            cv2.drawMarker(img, (xmoy, ymoy), (0,0,255))
        except:
            pass

        cv2.imshow("rendering", img)

        if cv2.waitKey(1) == ord('q'):
            go = False
            cv2.destroyWindow("rendering")
            
    #return percent value between -100,100 resp turn left,right
    return calc


#swap line detection
def swap(img):
    global d
    t = time.time()

    #check if swap can be operated
    if stamp[1] or (t - stamp[0] >= 5):
        stamp[1] = True
        #dropping the top of the image
        img[:300, :] = 0
        #remove imperfection with blur
        blur = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)
        #transform HSV
        hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        #set color range
        lower_range = colors[limit][0]
        upper_range = colors[limit][1]
        #masking
        mask = cv2.inRange(hsv_img, lower_range, upper_range)
        #detect real mark or artefact
        Y,X = np.where(mask != 0)
        if len(Y) > 1500:
            curr_col = (curr_col + 1) % 2 #change color
            stamp[1] = False #lock swap
            stamp[0] = t #remember last timestamp swap occured


if __name__ == "__main__":
    while go:
        image = capture()
        percent = compute(image)
        old_calc = percent
        print(percent, detect[curr_col], f"old : {old_calc}")
        swap(image)
    cam.release()
