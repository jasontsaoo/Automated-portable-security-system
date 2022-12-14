from keras.models import load_model
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
from random import choice

REV_CLASS_MAP = {
    0: "victory_sign",
    1: "nothing"
}

def mapper(val):
    return REV_CLASS_MAP[val]

def gameFunction(camera, model):
    
    REV_CLASS_MAP = {
        0: "victory_sign",
        1: "nothing"
    }
    
    while True:
        rawCapture = PiRGBArray(camera, size=(640, 480)) # grab the raw NumPy array representing the image
        camera.capture(rawCapture, format="bgr")
        frame = rawCapture.array
    
        cv2.rectangle(frame, (10, 70), (300, 340), (0, 255, 0), 2)
    
        # extract the region of image within the user rectangle
        roi = frame[70:300, 10:340]
        img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (227, 227))
    
        # predict the move made
        pred = model.predict(np.array([img]))
        move_code = np.argmax(pred[0])
        user_move_name = mapper(move_code)
        if user_move_name=="victory_sign":
            return True
        else:
            return False
    
        # display the information
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(frame, "hand sign: " + user_move_name,(10, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
        #cv2.imshow("hand sign", frame)
    
        k = cv2.waitKey(10)
        if k == ord('q'):
            break
    
