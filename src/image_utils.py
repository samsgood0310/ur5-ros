import time

import cv2
import numpy as np
from urllib import urlopen
import imutils

"""
This program provides convenience methods for everything related to Computer Vision: namely retrieving the image from 
the HTTP server, and finding the contour of the object.
"""

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)

def get_image():
    url = "http://192.168.178.193:4242/current.jpg?type=color"
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def get_center(contour):
    momt = cv2.moments(contour)
    area = int(momt["m00"])
    return int(momt["m10"] / area), int(momt["m01"] / area)


def get_cork_centroid(image):
    # Red iPhone
    # bgr = [62, 54, 191]

    # Blue tape
    # bgr = [102, 38, 4]

    # Orange
    bgr = [33, 74, 100]
    # Working
    # bgr = [25, 72, 213]

    # Yellow
    # bgr = [85, 207, 228]

    hsv_range = 20

    bgr_img = np.uint8([[bgr]])
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    hsv_value = hsv_img[0, 0, 0]

    lower = np.array([8, 143, 50])
    upper = np.array([32, 201, 255])

    # lower = np.array([8, 106, 48])
    # upper = np.array([32, 255, 255])

    try:

        # Read and resize image
        image = imutils.resize(image, width=600)

        # Convert image to HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create mask
        in_range_mask = cv2.inRange(hsv_image, lower, upper)
        # in_range_mask = cv2.inRange(hsv_image, minHSV, maxHSV)

        # Bitwise-AND mask and original image
        in_range_result = cv2.bitwise_and(image, image, mask=in_range_mask)

        # Convert to grayscale
        gs_image = cv2.cvtColor(in_range_result, cv2.COLOR_BGR2GRAY)

        # Get all contours
        _, contours, hierarchy = cv2.findContours(gs_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Remove small contours
        eligible = [c for c in contours if cv2.contourArea(c) >= 10]

        # Sort images
        ordered = sorted(eligible, key=lambda c: cv2.contourArea(c), reverse=True)

        center = None
        # Grab largest contour
        if len(ordered) > 0:
            largest = ordered[0]

            # Get bounding rectangle coordinates
            x, y, w, h = cv2.boundingRect(largest)

            # Draw a rectangle around contour
            cv2.rectangle(image, (x, y), (x + w, y + h), BLUE, 2)

            # Draw a bounding box around contour
            cv2.drawContours(image, [largest], -1, GREEN, 2)

            # Draw center of contour
            center_x, center_y = get_center(largest)
            cv2.circle(image, (center_x, center_y), 4, RED, -1)
            center = (center_x, center_y)
            # Add centroid to image text
    finally:
        cv2.destroyAllWindows()
    if not center:
        raise AssertionError("No contour found")
    else:
        return center

if __name__ == "__main__":
    try:
        while 1:
            last_time = time.time()
            image = get_image()

            cv2.imshow("image", get_image())

            cv2.waitKey(1)
            print(get_cork_centroid(image))
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()