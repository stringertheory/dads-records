import os
import cv2
import numpy as np
import sys
import time
import json
from PIL import Image
from icecream import ic
from mouse import make_out_filename
import numpy as np
import cv2

OUT_SIZE = 350

if __name__ == "__main__":
    filenames = sys.argv[1:]

    for filename in filenames:
        image = cv2.imread(filename)

        corners_filename = make_out_filename(filename, "manual", ".json")
        ic(corners_filename)
        if os.path.isfile(corners_filename):
            with open(corners_filename) as infile:
                corners = json.load(infile)

            S = corners[1][0] - corners[0][0]

            corners = np.float32(corners)
            square = np.float32([[0, 0], [S, 0], [S, S], [0, S]])
            matrix = cv2.getPerspectiveTransform(corners, square)
            result = cv2.warpPerspective(image, matrix, (S, S))
            size = (OUT_SIZE, OUT_SIZE)
        else:
            result = image
            h, w, c = image.shape
            size = (OUT_SIZE, int(OUT_SIZE * h / w))
            
        out_filename = make_out_filename(filename, "../records/", ".jpg", prefix="thumbs")
        ic(out_filename)
        
        # cv2.imshow("orig", image)
        # cv2.imshow("tran", result)
        # cv2.waitKey(0)

        rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        pil_image = pil_image.resize(size, Image.LANCZOS)
        pil_image.save(out_filename, optimize=True, quality=95)
        
