import cv2
import numpy as np
import sys


# adapted from https://paulbourke.net/geometry/pointlineplane/
def check_intersection(line1, line2, extend=False):
    a, b = line1
    c, d = line2
    x1, y1 = a["x"], a["y"]
    x2, y2 = b["x"], b["y"]
    x3, y3 = c["x"], c["y"]
    x4, y4 = d["x"], d["y"]

    # Check if any of the lines are of length 0
    if (x1 == x2 and y1 == y2) or (x3 == x4 and y3 == y4):
        return None

    denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

    # Lines are parallel (commenting out, because in this case they
    # never will be parallel)
    # if denominator == 0: return collinear_intersection(line1, line2)

    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

    # is the intersection along the segments
    if (not extend) and (ua < 0 or ua > 1 or ub < 0 or ub > 1):
        return None

    # Return x and y coordinates of the intersection
    return {"x": x1 + ua * (x2 - x1), "y": y1 + ua * (y2 - y1)}


def length(line):
    x1, y1, x2, y2 = line[0]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (slope * x1)
    length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
    print(slope)  # , intercept, length)
    if abs(slope) > 10 or abs(slope) < 0.1:
        return length
    else:
        return 0


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

def make_outer_lines(width, height, side, lines, skip=1):

    assert side in ["left", "right", "top", "bottom"]

    match side:
        case "left":
            s = height
            compare = min
            sweep = [{"x": 0, "y": None}, {"x": width, "y": None}]
            z = "y"
        case "right":
            s = height
            compare = max
            sweep = [{"x": 0, "y": None}, {"x": width, "y": None}]
            z = "y"
        case "top":
            s = width
            compare = min
            sweep = [{"x": None, "y": 0}, {"x": None, "y": height}]
            z = "x"
        case "bottom":
            s = width
            compare = max
            sweep = [{"x": None, "y": 0}, {"x": None, "y": height}]
            z = "x"
        case _:
            raise ValueError(f"invalid value for side {side!r}")

    print(compare)

    import collections
    outer_lines = collections.Counter()
    for i in range(0, s, skip):

        sweep[0][z] = i
        sweep[1][z] = i
        
        intersections = []
        for line_number, line in enumerate(lines):
            intersection = check_intersection(sweep, line["line"])
            if intersection:
                intersections.append((intersection["x"], line_number))

        if intersections:
            outer_line_number = compare(intersections, key=lambda i: i[0])[1]
            outer_lines[outer_line_number] += 1

    outer_lines = [(lines[i], n) for (i, n) in outer_lines.items()]
            
    return outer_lines

def weighted_average(points):
    import statistics
    x_sum = 0
    y_sum = 0
    n = 0
    xs = []
    ys = []
    for p, weight in points:
        x_sum += p["x"] * weight
        xs.extend([p["x"]] * weight)
        y_sum += p["y"] * weight
        ys.extend([p["y"]] * weight)
        n += weight
    # return {"x": x_sum / n, "y": y_sum / n}
    return {"x": statistics.median(xs), "y": statistics.median(ys)}

def corner(lines_a, lines_b):
    points = []
    for a, n_a in lines_a:
        for b, n_b in lines_b:
            p = check_intersection(a["line"], b["line"], extend=True)
            points.append((p, n_a * n_b))
    c = weighted_average(points)
    return (int(c["x"]), int(c["y"]))

def main():
    MIN_LINE_LENGTH = 10
    MIN_SLOPE = 10

    # Read gray image
    filename = sys.argv[1]

    # img = cv2.imread(filename, 0)
    color = cv2.imread(filename)
    h, w, channels = color.shape

    left_lines = []
    right_lines = []
    top_lines = []
    bottom_lines = []

    for img in cv2.split(color):
        # Create default parametrization LSD
        lsd = cv2.createLineSegmentDetector(0)

        # Detect lines in the image
        lines, width, prec, nfa = lsd.detect(img)

        for line in lines:
            info = line_type(line)
            # print(info)
            if info["length"] > MIN_LINE_LENGTH:
                if abs(info["slope"]) > MIN_SLOPE:
                    if info["x_max"] < (w / 2):
                        left_lines.append(info)
                    else:
                        right_lines.append(info)
                elif abs(info["slope"]) < (1 / MIN_SLOPE):
                    if info["y_max"] < (h / 2):
                        top_lines.append(info)
                    else:
                        bottom_lines.append(info)


    outer_left_lines = make_outer_lines(w, h, "left", left_lines, 1)
    outer_right_lines = make_outer_lines(w, h, "right", right_lines, 1)
    outer_top_lines = make_outer_lines(w, h, "top", top_lines, 1)
    outer_bottom_lines = make_outer_lines(w, h, "bottom", bottom_lines, 1)


    outer_left = np.array([i["np_line"] for i, n in outer_left_lines])
    outer_right = np.array([i["np_line"] for i, n in outer_right_lines])
    outer_top = np.array([i["np_line"] for i, n in outer_top_lines])
    outer_bottom = np.array([i["np_line"] for i, n in outer_bottom_lines])

    p = corner(outer_left_lines, outer_top_lines)
    drawn_img = lsd.drawSegments(color, outer_left)
    drawn_img = lsd.drawSegments(drawn_img, outer_top)
    drawn_img = cv2.circle(drawn_img, p, 12, (0, 255, 255), 4)
    cv2.imshow("HI", drawn_img)
    cv2.waitKey(0)

    p = corner(outer_left_lines, outer_bottom_lines)
    drawn_img = lsd.drawSegments(color, outer_left)
    drawn_img = lsd.drawSegments(drawn_img, outer_bottom)
    drawn_img = cv2.circle(drawn_img, p, 12, (0, 255, 255), 4)
    cv2.imshow("HI", drawn_img)
    cv2.waitKey(0)

    p = corner(outer_right_lines, outer_top_lines)
    drawn_img = lsd.drawSegments(color, outer_right)
    drawn_img = lsd.drawSegments(drawn_img, outer_top)
    drawn_img = cv2.circle(drawn_img, p, 12, (0, 255, 255), 4)
    cv2.imshow("HI", drawn_img)
    cv2.waitKey(0)

    p = corner(outer_right_lines, outer_bottom_lines)
    drawn_img = lsd.drawSegments(color, outer_right)
    drawn_img = lsd.drawSegments(drawn_img, outer_bottom)
    drawn_img = cv2.circle(drawn_img, p, 12, (0, 255, 255), 4)
    cv2.imshow("HI", drawn_img)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
