import cv2
import threading

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
        self._vcap = cv2.VideoCapture(address)

        if self.is_opened == False:
            raise FailedOpeningVideoError

        self._frame_lock = threading.Lock()
        self._current_frame = None
        self._read_thread = threading.Thread(target = self._readContinuous,
                                             name = 'read_thread')
        self._read_thread.setDaemon(True)
        self._read_thread.start()

    @property
    def is_opened(self):
        return self._vcap.isOpened()

    def _readContinuous(self):
        while (True):
            ret, frame = self._vcap.read()

            if ret == False:
                raise FailedReadFrameError

            with self._frame_lock:
                self._current_frame = frame

    def getCurrentFrame(self):
        with self._frame_lock:
            frame = self._current_frame

        return frame

if __name__ == '__main__':
    # cam = Camera(ADDRESS)
    cam = Camera(r'http://204.248.124.202/mjpg/video.mjpg')

    while(1):
        frame = cam.getCurrentFrame()

        if type(frame) != type(None):
            cv2.imshow('VIDEO', frame)

        if cv2.waitKey(100) == ord('q'):
            break