import cv2
import sys

image_filename = sys.argv[1]

def run_histogram_equalization(rgb_img):

    # convert from RGB color-space to YCrCb
    ycrcb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2YCrCb)

    # equalize the histogram of the Y channel
    ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])

    # convert back to RGB color-space from YCrCb
    return cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2BGR)


# load the image, display it to our screen, and construct a list of
# bilateral filtering parameters that we are going to explore
image = cv2.imread(image_filename)#, cv2.IMREAD_GRAYSCALE)

cv2.imshow("Original", image)

image = run_histogram_equalization(image)

cv2.imshow("Equalized", image)
cv2.waitKey(0)
    
params = [(61, 21, 7), (61, 41, 21), (61, 61, 39)]
params = [(11, 75, 75), (21, 75, 75), (31, 75, 75)]
# params = [(11, 75, 75), (21, 75, 75), (31, 75, 75), (41, 75, 75)]
params = [(10*i + 1, 75, 75) for i in range(1, 10)]
# loop over the diameter, sigma color, and sigma space
for (diameter, sigmaColor, sigmaSpace) in params:
    
    # apply bilateral filtering to the image using the current set of
    # parameters
    blurred = cv2.bilateralFilter(image, diameter, sigmaColor, sigmaSpace)
    # blurred = cv2.medianBlur(image, diameter)#, sigmaColor, sigmaSpace)
    # show the output image and associated parameters
    title = "Blurred d={}, sc={}, ss={}".format(diameter, sigmaColor, sigmaSpace)
    print(title)
    cv2.imshow("Blurred", blurred)
    cv2.waitKey(0)

    lsd = cv2.createLineSegmentDetector(0)
    
    # Detect lines in the image
    gray_blurred = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    lines, width, prec, nfa = lsd.detect(gray_blurred)
    drawn_img = lsd.drawSegments(gray_blurred, lines)
    # drawn_img = lsd.drawSegments(drawn_img, outer_top)
    # drawn_img = cv2.circle(drawn_img, p, 12, (0, 255, 255), 4)
    cv2.imshow("HI", drawn_img)
    cv2.waitKey(0)
    
    # thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                                cv2.THRESH_BINARY, diameter, 2)

    # cv2.imshow("Treshold", thresh)
    # cv2.waitKey(0)

    
    edges = cv2.Canny(image=blurred, threshold1=100, threshold2=200)

    # Display Canny Edge Detection Image
    cv2.imshow('Canny Edge Detection', edges)
    cv2.waitKey(0)
    
