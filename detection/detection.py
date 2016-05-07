import cv2
import itertools
import numpy as np
from scipy import ndimage
import math

IMG_PATH = 'cars_hsv_s_0.5_v_1.0.png'

DIFFERENT_COLORS = 7
HUE_MAX = 179


class Detector(object):
    def __init__(self):
        lower_bounds = [int(HUE_MAX * float(i)/DIFFERENT_COLORS) for i in range(DIFFERENT_COLORS)]
        upper_bounds = [int(HUE_MAX * float(i+1)/DIFFERENT_COLORS) - 1 for i in range(DIFFERENT_COLORS)]
        upper_bounds[-1] = HUE_MAX  # to include all possibilities

        self.color_array_boundaries = [(np.array([lower, 1, 1], dtype="uint8"),
                                        np.array([upper, 255, 255], dtype="uint8"))
                                       for lower, upper in zip(lower_bounds, upper_bounds)]

    def find_img_by_color_mask(self, hsv_img, color):
        # find the colors within the specified boundaries
        return cv2.inRange(hsv_img, self.color_array_boundaries[color][0],
                           self.color_array_boundaries[color][1])

    def find_target_mask(self, img, hsv_img, identifier):
        color_id1 = identifier[0]
        color_id2 = identifier[1]

        mask_color1 = self.find_img_by_color_mask(hsv_img, color_id1)
        mask_color2 = self.find_img_by_color_mask(hsv_img, color_id2)

        # create a mask of both colors
        color_combination_mask = cv2.bitwise_or(mask_color1, mask_color2)

        # for debugging original color mask, uncomment this
        # return color_combination_mask

        # classify colored regions into separate object markers
        _, markers = cv2.connectedComponents(color_combination_mask)

        # find the biggest colored region. the others are probably noise
        marker_sizes = np.bincount(markers[markers.nonzero()])
        if len(marker_sizes) == 0:
            biggest_marker = -1
        else:
            biggest_marker = np.argmax(marker_sizes)

        # transform to a mask leaving only the biggest marker-
        # biggest-marker => 255, the rest => 0
        biggest_marker_mask = np.zeros(img.shape[0:2], 'uint8')
        biggest_marker_mask[markers == biggest_marker] = 255

        return biggest_marker_mask

    def find_object_center(self, blob):
        # find the center of mass
        center = ndimage.measurements.center_of_mass(blob)

        return center

    def find_target(self, img, hsv_img, identifier):
        target_mask = self.find_target_mask(img, hsv_img, identifier)
        center = self.find_object_center(target_mask)

        return target_mask, center

    def find_all_targets(self, img, hsv_img):
        findings = []
        for combo in itertools.combinations(range(DIFFERENT_COLORS), 2):
            # TODO- only valid car combos
            findings.append(self.find_target(img, hsv_img, combo))

        return findings

    def display_markers(self, img, findings):
        for finding in findings:
            target_mask, center = finding

            # apply the mask, and fill the background white
            output = cv2.bitwise_and(img, img, mask=target_mask)
            output[0 == target_mask] = [255, 255, 255]

            if not math.isnan(center[1]) and not math.isnan(center[0]):
                cv2.drawMarker(output, (int(center[1]), int(center[0])),
                               color=[150, 150, 150], markerType=1, thickness=3,
                               markerSize=10)

            # show the images
            img_to_show = cv2.resize(img, (350, 700))
            output_to_show = cv2.resize(output, (350, 700))
            cv2.imshow("images", np.hstack([img_to_show, output_to_show]))
            cv2.waitKey(0)

if __name__ == '__main__':
    # load the image
    image = cv2.imread(IMG_PATH)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    detector = Detector()
    results = detector.find_all_targets(image, hsv)
    detector.display_markers(image, results)
