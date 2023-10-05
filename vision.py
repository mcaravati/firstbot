import subprocess
import sys
from time import time


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

DEBUG = True
go = True

#Colors limits
colors = {"black": [np.array([0, 0, 0]), np.array([180, 150, 90])]}
colors["green"] = [np.array([30, 50, 20]), np.array([65, 255, 255])]
colors["orange"] = [np.array([0, 20, 10]), np.array([20, 255, 255])]

#Witch color to detect
detect = ["black", "green"]
old_calc = 0
#Set swap color
limit = "orange"
stamp = [time(), False]

#Cam init
cam_port = 0 #TODO : change to 0 for Rasp
cam = cv2.VideoCapture(cam_port)
#Cam resolution
x_max = 160
y_max = 120
cam.set(cv2.CAP_PROP_FRAME_WIDTH, x_max)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, y_max)


#Capture image & return image to work with
def capture():
    _, img = cam.read()
    # img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


#Line detection
def compute(img):
    global go, old_calc

    #remove imperfection with blur
    # blur = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)
    img[:, (x_max - 60):, :] = 0
    #transform HSV
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #set color range
    lower_range = colors[detect[1]][0]
    upper_range = colors[detect[1]][1]
    #masking
    mask = cv2.inRange(hsv_img, lower_range, upper_range)
    #generate mask's skeleton
    # skeleton = skeletonize(mask, method="lee")
    edged = cv2.Canny(mask, 30, 200)

    #skeleton x,y mean
    Y, X = np.where(edged > 0)
    xmoy = x_max/2
    ymoy = y_max/2
    calc = old_calc
    try:
        xmoy = int(np.mean(X))
        ymoy = int(np.mean(Y))
        #normalize
        calc = max(min(((ymoy - (y_max/2)) / (y_max/200)), 80.0), -80.0)
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
            cv2.destroyAllWindows()
            
    #return percent value between -100,100 resp turn left,right
    return calc

def capture():
    _, img = cam.read()
    # img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img

#Line detection
def compute_black(img):
    global go, old_calc

    #remove imperfection with blur
    #transform HSV
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_img[:, (x_max - 50):] = 255
    #masking
    gray_img[gray_img < 90] = 0
    gray_img[gray_img >= 90] = 255
    gray_img = np.invert(gray_img)
    #generate mask's edge
    edged = cv2.Canny(gray_img, 30, 200)

    #skeleton x,y mean
    Y, X = np.where(edged > 0)
    xmoy = x_max/2
    ymoy = y_max/2
    calc = old_calc
    try:
        xmoy = int(np.mean(X))
        ymoy = int(np.mean(Y))
        #normalize
        calc = max(min(((ymoy - (y_max/2)) / (y_max/200)), 80.0), -80.0)
    except:
        pass

    #video debug
    if DEBUG :
        edged = cv2.Canny(gray_img, 30, 200)
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(gray_img, contours, -1, (0, 255, 255), 1)
        try:
            cv2.drawMarker(gray_img, (xmoy, ymoy), (0,0,255))
        except:
            pass

        cv2.imshow("rendering", gray_img)
        cv2.imshow("flat", img)

        if cv2.waitKey(1) == ord('q'):
            go = False
            cv2.destroyAllWindows()
            
    #return percent value between -100,100 resp turn left,right
    return calc


#swap line detection
def swap(img, curr_col):
    t = time()
    #check if swap can be operated
    if stamp[1] or (t - stamp[0] >= 5):
        stamp[1] = True
        #dropping the top of the image
        img[:, 40:] = 0
        #transform HSV
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #set color range
        lower_range = colors[limit][0]
        upper_range = colors[limit][1]
        #masking
        mask = cv2.inRange(hsv_img, lower_range, upper_range)
        #detect real mark or artefact
        Y,X = np.where(mask != 0)
        if len(Y) > 1500:
            curr_col = (curr_col + 1) % 2 #change color
            #curr_col = 1 #change color
            stamp[1] = False #lock swap
            stamp[0] = t #remember last timestamp swap occured
    return curr_col


if __name__ == "__main__":
    curr_col = 0
    while go:
        image = capture()
        percent = compute_black(image) if curr_col == 0 else compute(image)
        print(percent, detect[curr_col], f"old : {old_calc}")
        old_calc = percent
        swap(image)
    cam.release()