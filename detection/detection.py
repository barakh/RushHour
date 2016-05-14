import cv2
import itertools
import numpy as np
from scipy import ndimage
import math

# IMG_PATH = r'sample_images\cars_hsv_s_0.5_v_0.5_artificial.png'
IMG_PATH = r'sample_images\cars_hsv_s_0.5_v_0.5_photographed.png'

DIFFERENT_COLORS = 7
HUE_MAX = 179
MIN_CAR_SIZE = 200
MAX_CAR_SIZE = 4000
DILATION_KERNAL_SIZE = 5
DILATION_ITERATIONS = 4

DEBUG = False


class Detector(object):
    def __init__(self):
        lower_bounds = [int(HUE_MAX * float(i)/DIFFERENT_COLORS) for i in range(DIFFERENT_COLORS)]
        upper_bounds = [int(HUE_MAX * float(i+1)/DIFFERENT_COLORS) - 1 for i in range(DIFFERENT_COLORS)]
        upper_bounds[-1] = HUE_MAX  # to include all possibilities

        self.color_array_boundaries = [(np.array([lower, 50, 1], dtype="uint8"),
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

        # create a mask of both colors, eliminate small spaces
        color_combination_mask = cv2.bitwise_or(mask_color1, mask_color2)
        dilation_kernel = np.ones((DILATION_KERNAL_SIZE, DILATION_KERNAL_SIZE), np.uint8)
        color_combination_mask_dilated = cv2.dilate(color_combination_mask, dilation_kernel, DILATION_ITERATIONS)

        if DEBUG:
            self.display_images(mask_color1, mask_color2)
            self.display_images(color_combination_mask, color_combination_mask_dilated)
            return color_combination_mask

        # classify colored regions into separate object markers
        _, markers = cv2.connectedComponents(color_combination_mask_dilated)

        # create initial empty mask
        biggest_marker_mask = np.zeros(img.shape[0:2], 'uint8')

        # find the biggest colored region. the others are probably noise
        marker_sizes = np.bincount(markers[markers.nonzero()])
        marker_sizes[(marker_sizes < MIN_CAR_SIZE) | (marker_sizes > MAX_CAR_SIZE)] = -1
        if len(marker_sizes) == 0 or np.all(marker_sizes == -1):
            return biggest_marker_mask  # zeros- target not found
        biggest_marker = np.argmax(marker_sizes)

        # transform to a mask leaving only the biggest marker
        biggest_marker_mask[markers == biggest_marker] = 255
        return biggest_marker_mask

    def find_object_center(self, blob):
        # find the center of mass
        return ndimage.measurements.center_of_mass(blob)

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

    def start_color_picking(self, img, hsv = True):
        img_resized = cv2.resize(img, (300, 600))
        if hsv == True:
            self.image_color_pick = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
        else:
            self.image_color_pick = img_resized

        window_name = 'color_picking'
        cv2.imshow('color_picking', img_resized)

        cv2.setMouseCallback(window_name, self.mouse_callback)

        cv2.waitKey()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            color = self.image_color_pick[y,x]
            print '({}, {}) = {}'.format(x, y, color)

    def display_images(self, img1, img2):
        complete_image = np.hstack([img1, img2])
        cv2.imshow('Images', complete_image)
        cv2.waitKey()


if __name__ == '__main__':
    # load the image
    image = cv2.imread(IMG_PATH)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    detector = Detector()
    results = detector.find_all_targets(image, hsv)
    detector.display_markers(image, results)

    # detector = Detector()
    # detector.find_target_mask(image, hsv, [0,1])

    # detector = Detector()
    #
    # small = cv2.resize(image, (300, 600))
    # detector.start_color_picking(small)
    # cv2.imshow('0', small)
    #
    # for ind in range(DIFFERENT_COLORS):
    #     res = detector.find_img_by_color_mask(hsv, ind)
    #     small = cv2.resize(res, (300, 600))
    #     cv2.imshow('1', small)
    #
    #     cv2.waitKey(0)