import cv2
import numpy as np
import sys

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


MIN_LINE_LENGTH = 30
MIN_SLOPE = 10
LINE_WIDTH = 10

# Read gray image
filename = sys.argv[1]

# img = cv2.imread(filename, 0)
color = cv2.imread(filename)
h, w, channels = color.shape

line_image = np.copy(color) * 0  # creating a blank to draw lines on

for img in cv2.split(color):
    # Create default parametrization LSD
    lsd = cv2.createLineSegmentDetector(0)

    # Detect lines in the image
    lines, width, prec, nfa = lsd.detect(img)

    for line in lines:
        info = line_type(line)
        # print(info)
        x1, y1, x2, y2 = [int(round(i)) for i in line[0]]
        if info["length"] > MIN_LINE_LENGTH:
            if abs(info["slope"]) > MIN_SLOPE:
                if info["x_max"] < (w / 2):
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 255), LINE_WIDTH)
                else:
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 0), LINE_WIDTH)
            elif abs(info["slope"]) < (1 / MIN_SLOPE):
                if info["y_max"] < (h / 2):
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 255), LINE_WIDTH)
                else:
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), LINE_WIDTH)

lines_edges = cv2.addWeighted(color, 1, line_image, 0.8, 0)
cv2.imshow("IMAGE", lines_edges)
cv2.waitKey(0)
