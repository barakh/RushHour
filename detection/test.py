import numpy as np
import cv2
from scipy import ndimage

img_path = 'demoErrors.png'

# load the image
image = cv2.imread(img_path)

color_boundaries = [
    ([0, 0, 200], [50, 50, 255]),  # red
    ([0, 200, 0], [50, 255, 50]),  # green
    ([200, 0, 0], [255, 50, 50]),  # blue
    ([200, 0, 200], [255, 50, 255]),  # purple
    ([0, 200, 200], [50, 255, 255]),  # yellow
]

for (lower, upper) in color_boundaries:

    # create NumPy arrays from the boundaries
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    # find the colors within the specified boundaries
    in_color_mask = cv2.inRange(image, lower, upper)

    # classify colored regions into separate object markers
    _, markers = cv2.connectedComponents(in_color_mask)

    # find the biggest colored region. the others are probably noise
    biggest_marker = np.argmax(np.bincount(markers[markers.nonzero()]))

    # transform to a mask leaving only the biggest marker-
    # biggest-marker => 255, the rest => 0
    biggest_marker_mask = np.zeros(image.shape[0:2], 'uint8')
    biggest_marker_mask[markers == biggest_marker] = 255

    # apply the mask
    output = cv2.bitwise_and(image, image, mask=biggest_marker_mask)

    # find the center of mass and draw it
    center = ndimage.measurements.center_of_mass(biggest_marker_mask)
    cv2.drawMarker(output, (int(center[1]), int(center[0])), [255, 255, 255])

    # show the images
    cv2.imshow("images", np.hstack([image, output]))
    cv2.waitKey(0)
