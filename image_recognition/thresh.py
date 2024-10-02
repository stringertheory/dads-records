import cv2
import numpy as np
import sys

filename = sys.argv[1]
img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
img = cv2.medianBlur(img,3)
 
th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,21,2)
 
cv2.imshow("HI", th3)
cv2.waitKey(0)
 
