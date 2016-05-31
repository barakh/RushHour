import cv2
from detection import Detector
from camera import Camera
from get_positions import  HEIGHT_BOUNDS, WIDTH_BOUNDS

cam = Camera()
im_ind = 0

while(1):
        frame = cam.getCurrentFrame()

        if type(frame) != type(None):
            # Crop frame in order to filter out areas that are off of the white surface.
            frame = frame[HEIGHT_BOUNDS[0]:HEIGHT_BOUNDS[1], WIDTH_BOUNDS[0]:WIDTH_BOUNDS[1]]
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            detector = Detector()
            results = detector.find_all_targets(frame, hsv)
            detector.display_all_markers(frame, results)


        key = cv2.waitKey(100)

        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = 'screenshot_{:03d}.png'.format(im_ind)
            im_ind += 1
            cv2.imwrite(filename, frame)
