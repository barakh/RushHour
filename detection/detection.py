import cv2
import itertools
import numpy as np
from scipy import ndimage
from collections import OrderedDict

IMG_PATH = 'cars.png'

COLOR_BOUNDARIES = OrderedDict([
    ('blue', ([200, 0, 0], [255, 50, 50])),
    ('green', ([0, 200, 0], [50, 255, 50])),
    ('red', ([0, 0, 200], [50, 50, 255])),
    ('yellow', ([0, 200, 200], [50, 255, 255])),
    ('magenta', ([200, 0, 200], [255, 50, 255])),
    ('cyan', ([200, 200, 0], [255, 255, 50])),
    ('black', ([0, 0, 0], [50, 50, 50])),
])

class Detector(object):
    def __init__(self, color_boundries_dict):
        self.color_array_boundaries = {
            color: (np.array(lower, dtype="uint8"),
                    np.array(upper, dtype="uint8"))
            for (color, (lower, upper)) in color_boundries_dict.iteritems()}
        self.colors = color_boundries_dict.keys()

    def find_img_by_color_mask(self, img, color):
        '''find the colors within the specified boundaries'''
        if not self.color_array_boundaries.has_key(color):
            return None

        return cv2.inRange(img, self.color_array_boundaries[color][0],
                           self.color_array_boundaries[color][1])

    def find_target_mask(self, img, identifier):
        color1 = identifier[0]
        color2 = identifier[1]

        if not self.color_array_boundaries.has_key(color1):
            return None
        if not self.color_array_boundaries.has_key(color2):
            return None

        mask_color1 = self.find_img_by_color_mask(img, color1)
        mask_color2 = self.find_img_by_color_mask(img, color2)

        # create a mask of both colors
        color_combination_mask = cv2.bitwise_or(mask_color1, mask_color2)

        # classify colored regions into separate object markers
        _, markers = cv2.connectedComponents(color_combination_mask)

        # find the biggest colored region. the others are probably noise
        biggest_marker = np.argmax(np.bincount(markers[markers.nonzero()]))

        # transform to a mask leaving only the biggest marker-
        # biggest-marker => 255, the rest => 0
        biggest_marker_mask = np.zeros(img.shape[0:2], 'uint8')
        biggest_marker_mask[markers == biggest_marker] = 255

        return biggest_marker_mask

    def find_object_center(self, blob):
        # find the center of mass
        center = ndimage.measurements.center_of_mass(blob)

        return center

    def find_target(self, img, identifier):
        target_mask = self.find_target_mask(img, identifier)
        center = self.find_object_center(target_mask)

        return target_mask, center

    def find_all_targets(self, img):
        findings = []
        for combo in itertools.combinations(self.colors, 2):
            findings.append(self.find_target(img, combo))

        return findings

    def display_markers(self, img, findings):
        for finding in findings:
            target_mask, center = finding

            # apply the mask, and fill the background white
            output = cv2.bitwise_and(img, img, mask=target_mask)
            output[0 == target_mask] = [255, 255, 255]

            cv2.drawMarker(output, (int(center[1]), int(center[0])),
                           color=[150, 150, 150], markerType=1, thickness=3,
                           markerSize=10)

            # show the images
            cv2.imshow("images", np.hstack([img, output]))
            cv2.waitKey(0)

if __name__=='__main__':
    # load the image
    image = cv2.imread(IMG_PATH)
    detector = Detector(COLOR_BOUNDARIES)

    findings = detector.find_all_targets(image)
    detector.display_markers(image, findings)