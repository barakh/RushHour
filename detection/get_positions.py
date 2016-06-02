from detection import Detector
import cv2
from camera import Camera
import time

HEIGHT_BOUNDS = [20, -1]
WIDTH_BOUNDS = [85, -120]


class PositionsProvider(object):
    def __init__(self):
        self.cam = Camera()
        self.detector = Detector()

    def get_locations(self):
        frame = self.cam.getCurrentFrame()
        if type(frame) == type(None):
            return None

        # Crop frame in order to filter out areas that are off of the white surface.
        frame = frame[HEIGHT_BOUNDS[0]:HEIGHT_BOUNDS[1], WIDTH_BOUNDS[0]:WIDTH_BOUNDS[1]]

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        findings =  self.detector.find_all_targets(frame, hsv)
        result = []
        for _, center, dir in findings:
            if (self.detector.is_legal_point(center)
                and self.detector.is_legal_point(dir[0])
                and self.detector.is_legal_point(dir[1])):
                    result.append((center, dir))
            else:
                result.append(None)
        return result


p = PositionsProvider()
while True:
    print p.get_locations()
    time.sleep(0.1)
