import cv2
import threading
import time

WIFI_CAM_ADDRESS = 'rtsp://192.168.1.254/sjcam.mov'
STREET_CAM_STREAM = 'http://204.248.124.202/mjpg/video.mjpg' # God knows where
LAPTOP_CAM_ADDRESS = 0 # Device (builtin webcam)
ADDITIONAL_CAM_ADDRESS = 1 # Device (additional webcam, when connected by USB)

MAX_UP_TIME = 20 # sec

class FailedOpeningVideoError(Exception):
    pass

class FailedReadFrameError(Exception):
    pass

class Camera(object):
    ''' A class for reading frames from live camera, or a movie that
    runs in the background.
    '''
    def __init__(self, address = 0): #WIFI_CAM_ADDRESS):
        '''
        :param address: Integer for device, path for file, url for stream.
        '''
        self.address = address

        self._frame_lock = threading.Lock()
        self._current_frame = None

        self.startContinuousReadThread()
        self.startWatchdogThread()

    def startContinuousReadThread(self):
        # This thread continuously reads frames from the camera stream.
        # When cv2.VideoCapture.read is called, it returns the next frame,
        # not the latest. In order to get the latest frame, we
        # always read frames and throw them away.
        self._read_thread = threading.Thread(target = self._readContinuous,
                                             name = 'read_thread')
        self._read_thread.setDaemon(True)
        self._read_thread.start()

    def startWatchdogThread(self):
        self._watchdog_thread = threading.Thread(target = self._watchdog,
                                                 name = 'watchdog_thread')
        self._watchdog_thread.setDaemon(True)

        self._watchdog_kicked = False
        self._watchdog_thread.start()

    def _watchdog(self):
        time.sleep(10)
        while (True):
            time.sleep(2)

            if self._watchdog_kicked == False:
                print 'Bark! Read thread stuck.'
                print 'up_time = {}'.format(self.up_time)

                # print 'Bark! Read thread stuck. Restarting.'
                # # del self._read_thread
                # # del self._vcap
                #
                # self.startContinuousReadThread()
                # time.sleep(10)

            self._watchdog_kicked = False

    @property
    def is_opened(self):
        '''
        :return: True if stream is open, otherwise False.
        '''
        return self._vcap.isOpened()

    def _readContinuous(self):
        ''' "Silently" play a movie in blocking mode.
        (Read frames but don't display them).
        Normally runs in a thread that is owned by the class.
        '''
        print 'Starting capture'
        self._vcap = cv2.VideoCapture(self.address)
        start_time = time.time()
        self.up_time = 0

        if self.is_opened == False:
            raise FailedOpeningVideoError
        else:
            print "A" * 100
            open("temp", "wb").write(str(self.address))

        while (True):
            self._watchdog_kicked = True
            self.up_time = time.time() - start_time

            if (self.up_time > MAX_UP_TIME):
                print 'Starting capture'
                del self._vcap
                self._vcap = cv2.VideoCapture(self.address)
                start_time = time.time()
                self.up_time = 0

            ret, frame = self._vcap.read()

            if ret == False:
                print 'FailedReadFrameError'
                raise FailedReadFrameError

            with self._frame_lock:
                self._current_frame = frame

    def getCurrentFrame(self):
        '''
        :return: The latest frame from the stream.
        '''
        with self._frame_lock:
            frame = self._current_frame

        return frame

if __name__ == '__main__':
    cam = Camera(0)
    # cam = Camera(STREET_CAM_STREAM)

    im_ind = 0

    while(1):
        frame = cam.getCurrentFrame()

        if type(frame) != type(None):
            cv2.imshow('VIDEO', frame)

        key = cv2.waitKey(100)

        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = 'screenshot_{:03d}.png'.format(im_ind)
            im_ind += 1
            cv2.imwrite(filename, frame)
