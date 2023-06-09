import cv2
import time
import numpy as np
import numpy as np

def QRcode():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(5, 60)

    print(cap.get(5))
    
    while (cv2.waitKey(1) != 27):
        #_, frame = cap.read() #cv2.imread("stevecIzPozKam.jpg", cv2.IMREAD_COLOR)
        frame = cv2.imread("stevecIzPozKam.jpg", cv2.IMREAD_COLOR)
        
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(frame)

        # Draw rectangle around QR code on the frame
        if (points is not None):
            print(value)
            #300 323 001
            #300 323 002
            #300 323 003
        
        cv2.imshow("Image", frame)
    
        k = cv2.waitKey(1) & 0xff
        if k == 27 or k== ord('q'):
            break

if __name__ == "__main__":
    QRcode()