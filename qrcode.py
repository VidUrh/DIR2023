import cv2
import time
import numpy as np
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(5, 60)

print(cap.get(5))

while True:
    __, frame = cap.read()
    
    detect = cv2.QRCodeDetector()
    value, points, straight_qrcode = detect.detectAndDecode(frame)

    if (points is not None):
        print(value)
        #300 323 001
        #300 323 002
        #300 323 003
    
    cv2.imshow("Image", frame)
   
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()