import cv2
import time

# VID_PATH = r'd:\Projects\RushHour\30.Rock.S06E14.HDTV.x264-LOL.mp4'
VID_PATH = r'd:\Projects\RushHour\IMG_1928.MOV'

ADDRESS = 'rtsp://192.168.1.254/sjcam.mov'
# ADDRESS = 'http://204.248.124.202/mjpg/video.mjpg' # God knows where
# ADDRESS = 0 # Device (webcam)
# ADDRESS = 1 # Device (webcam)
# ADDRESS = VID_PATH

class FailedOpeningVideoError(Exception):
    pass

class FailedReadFrameError(Exception):
    pass

class Camera(object):
    def __init__(self, address = ADDRESS):
        self.vcap = cv2.VideoCapture(address)

        if self.is_opened == False:
            raise FailedOpeningVideoError

    @property
    def is_opened(self):
        return self.vcap.isOpened()

    def read(self):
        ret, frame = self.vcap.read()

        if ret == False:
            raise FailedReadFrameError

        return frame

if __name__ == '__main__':
    # cam = Camera(ADDRESS)
    cam = Camera(r'http://204.248.124.202/mjpg/video.mjpg')

    while(1):
        frame = cam.read()

        cv2.imshow('VIDEO', frame)
        if cv2.waitKey(1000) == ord('q'):
            break