import cv2
import itertools
import numpy as np
from scipy import ndimage
import math

# IMG_PATH = r'sample_images\cars_hsv_s_0.5_v_0.5_artificial.png'
# IMG_PATH = r'sample_images\cars_hsv_s_0.5_v_0.5_photographed.png'
IMG_PATH = r'..\screenshot_000.png'
# IMG_PATH = r'white.png'


DIFFERENT_COLORS = 4
HUE_MAX = 179
MIN_CAR_SIZE = 300
MAX_CAR_SIZE = 600
DILATION_KERNAL_SIZE = 5
DILATION_ITERATIONS = 4

DEBUG = True


class Detector(object):
    def __init__(self):
        # lower_bounds = [int(HUE_MAX * float(i)/DIFFERENT_COLORS) for i in range(DIFFERENT_COLORS)]
        # upper_bounds = [int(HUE_MAX * float(i+1)/DIFFERENT_COLORS) - 1 for i in range(DIFFERENT_COLORS)]
        # upper_bounds[-1] = HUE_MAX  # to include all possibilities

        # 4 colors- ~17, ~50-60, ~106, ~150
        lower_bounds = [10, 0, 105, 160]
        upper_bounds = [25, 0, 115, 170]
        self.color_array_boundaries = [(np.array([lower, 35, 1], dtype="uint8"),
                                        np.array([upper, 255, 255], dtype="uint8"))
                                       for lower, upper in zip(lower_bounds, upper_bounds)]
        self.color_ids = range(DIFFERENT_COLORS)
        # TODO- only valid car combos, ordered back-color -> front-color, i.e: [(1,2), (2,3)]
        # self.possible_cars = itertools.combinations(self.color_ids, 2)
        self.possible_cars = [(2,0), (0,3), (3,2)]

    def find_img_by_color_mask(self, hsv_img, color):
        # find the colors within the specified boundaries
        return cv2.inRange(hsv_img, self.color_array_boundaries[color][0],
                           self.color_array_boundaries[color][1])

    def find_target_mask(self, img, identifier, imgs_by_color_masks):
        color_id1 = identifier[0]
        color_id2 = identifier[1]

        mask_color1 = imgs_by_color_masks[color_id1]
        mask_color2 = imgs_by_color_masks[color_id2]

        # create a mask of both colors, eliminate small spaces
        color_combination_mask = cv2.bitwise_or(mask_color1, mask_color2)
        dilation_kernel = np.ones((DILATION_KERNAL_SIZE, DILATION_KERNAL_SIZE), np.uint8)
        color_combination_mask_dilated = cv2.dilate(color_combination_mask, dilation_kernel, DILATION_ITERATIONS)

        if DEBUG:
            pic_name = 'res\mask%s-%s.png' % (color_id1, color_id2)
            self.show_mask(img, color_combination_mask_dilated, pic_name)

        # classify colored regions into separate object markers
        _, markers = cv2.connectedComponents(color_combination_mask_dilated)

        # create initial empty mask
        biggest_marker_mask = np.zeros(img.shape[0:2], 'uint8')

        # find the biggest colored region. the others are probably noise
        marker_sizes = np.bincount(markers[markers.nonzero()])
        marker_sizes[(marker_sizes < MIN_CAR_SIZE) | (marker_sizes > MAX_CAR_SIZE)] = -1
        if len(marker_sizes) == 0 or np.all(marker_sizes == -1):
            # zeros- target not found
            return biggest_marker_mask, biggest_marker_mask, biggest_marker_mask
        biggest_marker = np.argmax(marker_sizes)

        # transform to a mask leaving only the biggest marker
        biggest_marker_mask[markers == biggest_marker] = 255

        # get the "winning" masks for each color separately (to find direction)
        color1_selected_mask = cv2.bitwise_and(mask_color1, biggest_marker_mask)
        color2_selected_mask = cv2.bitwise_and(mask_color2, biggest_marker_mask)
        return biggest_marker_mask, color1_selected_mask, color2_selected_mask

    def find_object_center(self, blob):
        # find the center of mass
        return ndimage.measurements.center_of_mass(blob)

    def find_target(self, img, identifier, imgs_by_color_masks):
        target_mask, color1_mask, color2_mask = self.find_target_mask(img, identifier, imgs_by_color_masks)
        center = self.find_object_center(target_mask)
        color1_center = self.find_object_center(color1_mask)
        color2_center = self.find_object_center(color2_mask)

        return target_mask, center, [color1_center, color2_center]

    def find_all_targets(self, img, hsv_img):
        imgs_by_color_masks = [self.find_img_by_color_mask(hsv_img, color_id) for color_id in self.color_ids]
        if DEBUG:
            self.show_all_masks(img, imgs_by_color_masks)
        findings = []
        for combo in self.possible_cars:
            findings.append(self.find_target(img, combo, imgs_by_color_masks))

        return findings

    def show_all_masks(self, img, masks):
        for i, mask in enumerate(masks):
            self.show_mask(img, mask, 'res\mask%s.png' % i)


    def show_mask(self, img, mask, pic_name = None):
        output = cv2.bitwise_and(img, img, mask=mask)
        output[0 == mask] = [255, 255, 255]
        stacked = np.hstack([img, output])
        if pic_name == None:
            cv2.imshow("masks", stacked)
            cv2.waitKey(0)
        else:
            cv2.imwrite(pic_name, stacked)

    def display_separate_markers(self, img, findings, resize=False):
        for finding in findings:
            target_mask, center, direction = finding

            # apply the mask, and fill the background white
            output = cv2.bitwise_and(img, img, mask=target_mask)
            output[0 == target_mask] = [255, 255, 255]

            self.show_center_and_direction(center, direction, output)

            # show the images
            if resize:
                img = cv2.resize(img, (350, 700))
                output  = cv2.resize(output, (350, 700))
            cv2.imshow("images", np.hstack([img, output]))

            cv2.waitKey(0)

    def display_all_markers(self, img, findings):
        total_mask = 0
        for finding in findings:
            target_mask, _, _ = finding
            total_mask = cv2.bitwise_or(total_mask, target_mask)

        # apply the mask, and fill the background white
        output = cv2.bitwise_and(img, img, mask=total_mask)
        output[0 == total_mask] = [255, 255, 255]

        for finding in findings:
            _, center, direction = finding
            self.show_center_and_direction(center, direction, output)

        stacked = np.hstack([img, output])
        if DEBUG:
            cv2.imwrite(r'res\result.png', stacked)
        cv2.imshow("images", stacked)

    def show_center_and_direction(self, center, direction, output):
        if self.is_legal_point(center):
            # show the car center
            cv2.drawMarker(output, self.point_to_display(center),
                           color=[150, 150, 150], markerType=1, thickness=3,
                           markerSize=10)
        if self.is_legal_point(direction[0]) and self.is_legal_point(direction[1]):
            # show the direction
            cv2.line(output, self.point_to_display(direction[0]),
                     self.point_to_display(direction[1]), [255, 255, 255], 2)
            # mark the head
            cv2.drawMarker(output, self.point_to_display(direction[1]),
                           color=[255, 255, 255], markerType=2, thickness=2,
                           markerSize=7)

    def is_legal_point(self, point):
        return not math.isnan(point[0]) and not math.isnan(point[1])

    def point_to_display(self, point):
        return int(point[1]), int(point[0])

    def start_color_picking(self, img, hsv = True):
        if hsv == True:
            self.image_color_pick = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        else:
            self.image_color_pick = img

        window_name = 'color_picking'
        cv2.imshow('color_picking', img)

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
    detector.display_all_markers(image, results)
    cv2.waitKey(0)

    # For color picking, uncomment:
    # detector = Detector()
    detector.start_color_picking(image)
    cv2.imshow('0', image)
    cv2.waitKey(0)