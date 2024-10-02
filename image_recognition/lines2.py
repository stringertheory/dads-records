import cv2
import numpy as np
import sys

from lines import check_intersection

def line_type(line):
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


MIN_LINE_LENGTH = 20
MIN_SLOPE = 10
LINE_WIDTH = 10

# Read gray image
filename = sys.argv[1]

# img = cv2.imread(filename, 0)
color = cv2.imread(filename)
h, w, channels = color.shape

line_image = np.copy(color) * 0  # creating a blank to draw lines on
# line_sum = np.copy(color) * 0  # creating a blank to draw lines on
line_sum = np.zeros(color.shape, np.float64)

left = [{"x": 0, "y": 0}, {"x": 0, "y": h}]
right = [{"x": w, "y": 0}, {"x": w, "y": h}]
top = [{"x": 0, "y": 0}, {"x": w, "y": 0}]
bottom = [{"x": 0, "y": h}, {"x": w, "y": h}]

for img in cv2.split(color):
    # Create default parametrization LSD
    lsd = cv2.createLineSegmentDetector(0)

    # img = cv2.medianBlur(img,11)
    # img = cv2.medianBlur(img,3)
    # img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #     cv2.THRESH_BINARY,11,2)
    # img = cv2.Canny(img, 10, 245)
    # cv2.imshow("IMAGE", img)
    # cv2.waitKey(0)
    
    # Detect lines in the image
    lines, width, prec, nfa = lsd.detect(img)

    for line in lines:
        info = line_type(line)
        # print(info)
        x1, y1, x2, y2 = [int(round(i)) for i in line[0]]
        if info["length"] > MIN_LINE_LENGTH:
            intensity = np.array([info["length"]] * 3).astype(np.float64)
            # print(intensity.astype(np.float64))
            # print(info["length"], intensity)
            
            if abs(info["slope"]) > MIN_SLOPE:

                # WHAT I WANT HERE
                """
                extend each line to the edge of the image
                add some jitter in the angle to make a "bowtie" shape to account for continuing lines (this will give higher weight to longer lines)
                add up all these to create an image that is the sum of all the bowties
                use an absolute threshold on the sum-of-bowtie images to create an image with only strong horizontal and vertical lines
                maybe need to line-detect again on this image to fine the outermost final lines
                """
                
                # t = check_intersection(info["line"], top, extend=True)
                # b = check_intersection(info["line"], bottom, extend=True)
                # x1l, y1l = int(round(t["x"])), int(round(t["y"]))
                # x2l, y2l = int(round(b["x"])), int(round(b["y"]))
                # blank = np.zeros(color.shape, np.float64)
                # cv2.line(blank, (x1l, y1l), (x2l, y2l), intensity, LINE_WIDTH)
                # line_sum += blank
                # cv2.imshow("IMAGE", line_sum)
                # cv2.waitKey(0)
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), LINE_WIDTH)
                if info["x_max"] < (w / 2):
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 255), LINE_WIDTH)
                elif info["x_max"] > (1 * w / 2):
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 0), LINE_WIDTH)
            elif abs(info["slope"]) < (1 / MIN_SLOPE):

                
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), LINE_WIDTH)
                if info["y_max"] < (h / 2):
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 255), LINE_WIDTH)
                elif info["y_max"] > (1 * h / 2):
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), LINE_WIDTH)
                    l = check_intersection(info["line"], left, extend=True)
                    r = check_intersection(info["line"], right, extend=True)
                    x1l, y1l = int(round(l["x"])), int(round(l["y"]))
                    x2l, y2l = int(round(r["x"])), int(round(r["y"]))
                    blank = np.zeros(color.shape, np.float64)
                    cv2.line(blank, (x1l, y1l), (x2l, y2l), intensity, LINE_WIDTH)
                    line_sum += blank

    # line_sum = np.clip(line_sum, [0, 0, 0], [255, 255, 255]).astype(np.uint8)
    cv2.imshow("IMAGE", img)
    cv2.waitKey(0)

line_sum = line_sum.astype(np.uint8)
cv2.imshow("IMAGE", line_sum)
cv2.waitKey(0)
    
lines_edges = cv2.addWeighted(color, 1, line_image, 0.8, 0)
cv2.imshow("IMAGE", lines_edges)
cv2.waitKey(0)
