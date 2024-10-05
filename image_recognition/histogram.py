import os
import sys
import glob
import numpy as np
import cv2

def run_histogram_equalization(rgb_img):

    # convert from RGB color-space to YCrCb
    ycrcb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2YCrCb)

    # equalize the histogram of the Y channel
    ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])

    # convert back to RGB color-space from YCrCb
    return cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2BGR)


# import all image files with the .jpg extension
image_filename = sys.argv[1]
image = cv2.imread(image_filename)

image = run_histogram_equalization(image)

cv2.imshow("histo", image)
cv2.waitKey(0)
