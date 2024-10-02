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

def line_info(line):
    x1, y1, x2, y2 = line[0]
    if x2 == x1:
        slope = np.inf
    else:
        slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (slope * x1)
    length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
    return {
        "np_line": line,
        "line": [{"x": x1, "y": y1}, {"x": x2, "y": y2}],
        "slope": slope,
        "intercept": intercept,
        "length": length,
        "x_min": min(x1, x2),
        "x_max": max(x1, x2),
        "y_min": min(y1, y2),
        "y_max": max(y1, y2),
    }

# import all image files with the .jpg extension
images = sys.argv[1:]

image_data = []
blurred_data = []
for img in images:
    this_image = cv2.imread(img, 1)
    blurred = cv2.medianBlur(this_image, 101)
    blurred_data.append(blurred)
    image_data.append(this_image)

avg_image = blurred_data[0]
for i in range(len(blurred_data)):
    if i == 0:
        pass
    else:
        alpha = 1.0/(i + 1)
        beta = 1.0 - alpha
        avg_image = cv2.addWeighted(blurred_data[i], alpha, avg_image, beta, 0.0)

cv2.imshow("BBOX", avg_image)
cv2.waitKey(0)

lsd = cv2.createLineSegmentDetector(0)

# Detect lines in the image
for image in image_data:
    image3 = cv2.absdiff(image, avg_image)
    # image3 = run_histogram_equalization(image3)
    all_lines = []
    for img in cv2.split(image3):
        gray = np.float32(img)
        dst = cv2.goodFeaturesToTrack(gray, 27, 0.01, 10) 

        # dst = cv2.cornerHarris(gray, 5, 3, 0.04)
        dst = np.intp(dst)

        for i in dst:
            print(i.ravel())
            x, y = i.ravel() 
            cv2.circle(img, (x, y), 3, 255, -1) 

        # cv2.imshow('BBOX',img)
        # cv2.waitKey(0)
        
        lines, width, prec, nfa = lsd.detect(img)
        for line in lines:
            info = line_info(line)
            if info["length"] > 3:
                if info["slope"] > 10 or info["slope"] < 1 / 10:
                    all_lines.extend(line)

    all_lines = np.array(all_lines)
    drawn_img = lsd.drawSegments(image, all_lines)
    cv2.imshow("BBOX", drawn_img)
    cv2.waitKey(0)
    

 
