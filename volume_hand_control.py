'''
This Module is resposible to adjust the computer volume by hands moviment
'''
# Basic Imports
import numpy as np
import cv2
import mediapipe as mp
import time
import math
import src.HandTrackingModule as htm

# Pycaw imports
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Camera size
wcam, hcam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)
detector = htm.handDetector()

# Pycaw to control the volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0, None) # Set volume to 100%

# Get Min and Max volume
minVol = volRange[0]
maxVol = volRange[1]

# Initialize variable params
vol = 0
volPer = 0
volBar = 400
previous_time = 0

while True:
    success, img = cap.read() # get status and frame
    img = detector.find_hands(img) # call the detector
    lmList = detector.find_positions(img, draw=False) # call the findpositions

    if len(lmList) != 0: # if there are finded position
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2) // 2, (y1+y2) // 2

        cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        length = math.hypot(x2 - x1, y2 - y1) # Hand Range

        # Hand range is 50 ~ 250, this may alter depending of your hand size
        # Volume Range -48 ~ 12, may change according your computer

        vol = np.interp(length, [50, 250], [minVol, maxVol])
        volBar = np.interp(length, [50, 250], [400, 150])
        print(volBar)
        volPer = np.interp(length, [50, 250], [0, 100])

        # Set the volume into computer, according detected hands
        # print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        # If the position is minimum, then draw a circle in the midle
        if length < 50:
            cv2.circle(img, (cx, cy), 7, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 255, 255), 3)
    
    # Change the bar color according to the volume percentage
    if int(volPer) > 75:
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0),
                    cv2.FILLED)
    elif int(volPer) > 50:
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 255, 0),
                    cv2.FILLED)
    else:
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255),
                    cv2.FILLED)                
    cv2.putText(img, f'{int(volPer)} %', (40, 450),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    # Show FPS info
    current_time = time.time()
    fps = 1/(current_time-previous_time)
    previous_time = current_time

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70),
                 cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)    
    cv2.imshow('Gesture volume control', img)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
