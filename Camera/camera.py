import cv2
import vlc
import time

# VID_PATH = r'test.mp4'
# VID_PATH = r'd:\Projects\RushHour\30.Rock.S06E14.HDTV.x264-LOL.mp4'
VID_PATH = r'd:\Projects\RushHour\IMG_1928.MOV'

command = []

ADDRESS = 'rtsp://192.168.1.254/sjcam.mov'
# ADDRESS = 'http://204.248.124.202/mjpg/video.mjpg' # God knows where
# ADDRESS = 0 # Device (webcam)
# ADDRESS = 1 # Device (webcam)
# ADDRESS = VID_PATH

# i = vlc.Instance('--verbose 2'.split())
# p = i.media_player_new()
# p.set_mrl(ADDRESS)
# # p.play()
#
# while(1):
#     p.next_frame()
#     # time.sleep(1)
#     if cv2.waitKey(1) == ord('q'):
#         break

vcap = cv2.VideoCapture(ADDRESS)

if vcap.isOpened() == False:
    print 'Failed to open stream.'

while(1):
    ret, frame = vcap.read()

    if ret != True:
        print 'Failed to get image.'
        break

    cv2.imshow('VIDEO', frame)
    if cv2.waitKey(1) == ord('q'):
        break

print 'Bye!!!!'