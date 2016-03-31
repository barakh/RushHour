import numpy as np
import cv2
from scipy import ndimage

img_path = 'cars.png'

color_boundaries = {
    'blue': ([200, 0, 0], [255, 50, 50]),
    'green': ([0, 200, 0], [50, 255, 50]),
    'red': ([0, 0, 200], [50, 50, 255]),
    'yellow': ([0, 200, 200], [50, 255, 255]),
    'magenta': ([200, 0, 200], [255, 50, 255]),
    'cyan': ([200, 200, 0], [255, 255, 50]),
    'black': ([0, 0, 0], [50, 50, 50]),
}

color_array_boundaries = {
    color: (np.array(lower, dtype="uint8"), np.array(upper, dtype="uint8"))
    for (color, (lower, upper)) in color_boundaries.iteritems()}

colors = color_boundaries.keys()


# find the colors within the specified boundaries
def get_img_color_mask(img, color):
    return cv2.inRange(img, color_array_boundaries[color][0], color_array_boundaries[color][1])

# load the image
image = cv2.imread(img_path)

for color1 in colors:
    mask_color1 = get_img_color_mask(image, color1)
    for color2 in colors:

        if color1 == color2:
            continue  # looking only for pairs of colors

        mask_color2 = get_img_color_mask(image, color2)

        # create a mask of both colors
        color_combination_mask = cv2.bitwise_or(mask_color1, mask_color2)

        # classify colored regions into separate object markers
        _, markers = cv2.connectedComponents(color_combination_mask)

        # find the biggest colored region. the others are probably noise
        biggest_marker = np.argmax(np.bincount(markers[markers.nonzero()]))

        # transform to a mask leaving only the biggest marker-
        # biggest-marker => 255, the rest => 0
        biggest_marker_mask = np.zeros(image.shape[0:2], 'uint8')
        biggest_marker_mask[markers == biggest_marker] = 255

        # apply the mask, and fill the background white
        output = cv2.bitwise_and(image, image, mask=biggest_marker_mask)
        output[0 == biggest_marker_mask] = [255, 255, 255]

        # find the center of mass and draw it
        center = ndimage.measurements.center_of_mass(biggest_marker_mask)
        cv2.drawMarker(output, (int(center[1]), int(center[0])),
                       color=[150, 150, 150], markerType=1, thickness=3, markerSize=10)

        # show the images
        cv2.imshow("images", np.hstack([image, output]))
        cv2.waitKey(0)
