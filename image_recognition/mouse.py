import os
import cv2
import numpy as np
import sys
import time
import json

from icecream import ic

import numpy as np
import cv2

# ============================================================================

CANVAS_SIZE = (600, 800)

FINAL_LINE_COLOR = (255, 255, 255)
WORKING_LINE_COLOR = (128, 196, 255)

# ============================================================================

def make_out_filename(image_path, out_dir, ext=None, prefix=""):
    out_parts = image_path.split("/")
    batch = out_parts[-2]
    basename = out_parts[-1]
    out_dir = os.path.join(out_dir, batch)
    os.makedirs(out_dir, exist_ok=True)
    out_filename = os.path.join(out_dir, prefix, basename)
    if ext:
        base, old_ext = os.path.splitext(out_filename)
        out_filename = base + ext
    return out_filename


class PolygonDrawer(object):
    def __init__(self):
        self.window_name = "image"
        self.done = False
        self.current = (0, 0)
        self.points = []

    def on_mouse(self, event, x, y, buttons, user_param):
        if self.done:
            return

        if event == cv2.EVENT_MOUSEMOVE:
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            print(
                "Adding point #%d with position(%d,%d)"
                % (len(self.points), x, y)
            )
            self.points.append((x, y))
        # elif event == cv2.EVENT_RBUTTONDOWN:
        #     print("Completing polygon with %d points." % len(self.points))
        #     self.done = True
        if len(self.points) >= 4:
            self.done = True
            
    def run(self, image_filename):
        color = cv2.imread(filename)
        
        cv2.namedWindow(self.window_name)
        cv2.imshow(self.window_name, color)
        cv2.waitKey(1)
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        while not self.done:
            # This is our drawing loop, we just continuously draw new images
            # and show them in the named window
            canvas = color.copy()
            if len(self.points) > 0:
                # Draw all the current polygon segments
                for point in self.points:
                    cv2.circle(
                        canvas, point, 10, FINAL_LINE_COLOR, 3
                    )
                    
                cv2.polylines(
                    canvas, np.array([self.points]), False, FINAL_LINE_COLOR, 3
                )
                # And  also show what the current segment would look like
                cv2.line(
                    canvas, self.points[-1], self.current, WORKING_LINE_COLOR, 3
                )
            cv2.imshow(self.window_name, canvas)
            if cv2.waitKey(50) == 27:  # ESC hit
                self.done = True

        # User finised entering the polygon points, so let's make the
        # final drawing of a filled polygon
        if len(self.points) > 0:
            cv2.fillPoly(canvas, np.array([self.points]), FINAL_LINE_COLOR)

        cv2.imshow(self.window_name, canvas)
        time.sleep(0.5)

        cv2.destroyWindow(self.window_name)
        return self.points


# ============================================================================

if __name__ == "__main__":

    filenames = sys.argv[1:]

    for filename in filenames:
        pd = PolygonDrawer()
        points = pd.run(filename)
        if len(points) == 4:
            out_filename = make_out_filename(filename, "manual", ".json")
            with open(out_filename, "w") as outfile:
                json.dump(points, outfile)



