import cv2
import numpy as np
import sys

from lines import check_intersection

def line_type(line):
    x1, y1, x2, y2 = line[0]
    length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
    if x2 == x1:
        y_slope = np.inf
    else:
        y_slope = (y2 - y1) / (x2 - x1)
    y_intercept = y1 - (y_slope * x1)
    if y2 == y1:
        x_slope = np.inf
    else:
        x_slope = (x2 - x1) / (y2 - y1)
    x_intercept = x1 - (x_slope * y1)
    return {
        "np_line": line,
        "line": [{"x": x1, "y": y1}, {"x": x2, "y": y2}],
        "y_slope": y_slope,
        "y_intercept": y_intercept,
        "x_slope": x_slope,
        "x_intercept": x_intercept,
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
# line_sum = np.copy(color) * 0  # creating a blank to draw lines on
left_linesum = np.zeros(color.shape, np.float64)
right_linesum = np.zeros(color.shape, np.float64)
top_linesum = np.zeros(color.shape, np.float64)
bottom_linesum = np.zeros(color.shape, np.float64)
left_lines = []
right_lines = []
top_lines = []
bottom_lines = []

left = [{"x": 0, "y": 0}, {"x": 0, "y": h}]
right = [{"x": w, "y": 0}, {"x": w, "y": h}]
top = [{"x": 0, "y": 0}, {"x": w, "y": 0}]
bottom = [{"x": 0, "y": h}, {"x": w, "y": h}]

for img in cv2.split(color):

    lsd = cv2.createLineSegmentDetector(0)
    lines, width, prec, nfa = lsd.detect(img)

    for line in lines:
        info = line_type(line)
        if info["length"] > MIN_LINE_LENGTH:
            x1, y1, x2, y2 = [int(round(i)) for i in line[0]]
            intensity = (50, 50, 50)
            if abs(info["y_slope"]) > MIN_SLOPE:
                
                # WHAT I WANT HERE
                """
                sum up all the lines into an line-sum image
                then for each detected line segment, look at the extended line and count the number of "on" pixels. include it in output if the count > some threshold. Find the outermost line.
                """
                
                blank = np.zeros(color.shape, np.float64)
                cv2.line(blank, (x1, y1), (x2, y2), intensity, LINE_WIDTH, cv2.LINE_AA)
                if info["x_max"] < (w / 2):
                    left_linesum += blank
                    left_lines.append(info)
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 255), LINE_WIDTH)
                elif info["x_max"] > (1 * w / 2):
                    right_linesum += blank
                    right_lines.append(info)
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 0), LINE_WIDTH)
            elif abs(info["y_slope"]) < (1 / MIN_SLOPE):

                blank = np.zeros(color.shape, np.float64)
                cv2.line(blank, (x1, y1), (x2, y2), intensity, LINE_WIDTH, cv2.LINE_AA)
                
                if info["y_max"] < (h / 2):
                    top_linesum += blank
                    top_lines.append(info)
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 255), LINE_WIDTH)
                elif info["y_max"] > (1 * h / 2):
                    bottom_linesum += blank
                    bottom_lines.append(info)
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), LINE_WIDTH)

def sum_along_line(line, linesum):
    h, w, _ = linesum.shape
    result = 0
    if abs(line["x_slope"]) < abs(line["y_slope"]):
        # print('vertical')
        for y in range(h):
            x = line["x_slope"] * y + line["x_intercept"]
            try:
                z = linesum[y][int(round(x))]
            except IndexError:
                continue
            result += z
    else:
        # print('horizontal')
        for x in range(w):
            y = line["y_slope"] * x + line["y_intercept"]
            try:
                z = linesum[int(round(y))][x]
            except IndexError:
                continue
            result += z
    return result[0]

threshold = 1000
g_line_image = np.copy(color) * 0  # creating a blank to draw lines on
g_width = 3

for line in left_lines:
    score = sum_along_line(line, left_linesum)
    if score > threshold:
        t = check_intersection(line["line"], top, extend=True)
        b = check_intersection(line["line"], bottom, extend=True)
        x1l, y1l = int(round(t["x"])), int(round(t["y"]))
        x2l, y2l = int(round(b["x"])), int(round(b["y"]))
        intense = (int(score / 1000), 0, int(score / 1000))
        cv2.line(g_line_image, (x1l, y1l), (x2l, y2l), intense, g_width, cv2.LINE_AA)

for line in top_lines:
    score = sum_along_line(line, top_linesum)
    if score > threshold:
        t = check_intersection(line["line"], left, extend=True)
        b = check_intersection(line["line"], right, extend=True)
        x1l, y1l = int(round(t["x"])), int(round(t["y"]))
        x2l, y2l = int(round(b["x"])), int(round(b["y"]))
        intense = (int(score / 1000), int(score / 1000), 0)
        # intense = (int(score / 1000), 0, int(score / 1000))
        cv2.line(g_line_image, (x1l, y1l), (x2l, y2l), intense, g_width, cv2.LINE_AA)

for line in right_lines:
    score = sum_along_line(line, right_linesum)
    if score > threshold:
        t = check_intersection(line["line"], top, extend=True)
        b = check_intersection(line["line"], bottom, extend=True)
        x1l, y1l = int(round(t["x"])), int(round(t["y"]))
        x2l, y2l = int(round(b["x"])), int(round(b["y"]))
        intense = (0, int(score / 1000), int(score / 1000))
        intense = (int(score / 1000), 0, int(score / 1000))
        cv2.line(g_line_image, (x1l, y1l), (x2l, y2l), intense, g_width, cv2.LINE_AA)

for line in bottom_lines:
    score = sum_along_line(line, bottom_linesum)
    if score > threshold:
        t = check_intersection(line["line"], left, extend=True)
        b = check_intersection(line["line"], right, extend=True)
        x1l, y1l = int(round(t["x"])), int(round(t["y"]))
        x2l, y2l = int(round(b["x"])), int(round(b["y"]))
        intense = (int(score / 1000), int(score / 1000), int(score / 1000))
        intense = (int(score / 1000), 0, int(score / 1000))
        cv2.line(g_line_image, (x1l, y1l), (x2l, y2l), intense, g_width, cv2.LINE_AA)

im = cv2.addWeighted(color, 1, g_line_image, 0.5, 0)
cv2.imshow("IMAGE", im)
cv2.waitKey(0)
        
# cv2.imshow("IMAGE", g_line_image)
# cv2.waitKey(0)

# for line in top_lines:
#     score = sum_along_line(line, left_linesum)
# left_linesum = left_linesum.astype(np.uint8)
# cv2.imshow("IMAGE", left_linesum)
# cv2.waitKey(0)

# right_linesum = right_linesum.astype(np.uint8)
# cv2.imshow("IMAGE", right_linesum)
# cv2.waitKey(0)

# top_linesum = top_linesum.astype(np.uint8)
# cv2.imshow("IMAGE", top_linesum)
# cv2.waitKey(0)

# bottom_linesum = bottom_linesum.astype(np.uint8)
# cv2.imshow("IMAGE", bottom_linesum)
# cv2.waitKey(0)

lines_edges = cv2.addWeighted(color, 1, line_image, 0.5, 0)
cv2.imshow("IMAGE", lines_edges)
cv2.waitKey(0)
