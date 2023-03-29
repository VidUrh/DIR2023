import cv2
import time
import numpy as np

def zaznavanjeKartona():
    pass

def zaznavanjeStevca():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(5, 60)

    print(cap.get(5))

    minHsvS = np.array([0, 0, 165])
    maxHsvS = np.array([180, 255, 220])

    while (cv2.waitKey(1) != 27):
        __, frame = cap.read()
        
        cv2.blur(frame, (7, 7))
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        #cv2.imshow("HSV", hsv)
        maskS = cv2.inRange(hsv, minHsvS, maxHsvS)
        cv2.erode(maskS, None, iterations=2)
        cv2.dilate(maskS, None, iterations=2)
        contours, hierarchy = cv2.findContours(maskS, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if (contours is not None and len(contours) > 0):
            maxContourSize = 0
            for i in contours:
                if cv2.contourArea(i) > maxContourSize:
                    maxContourSize = cv2.contourArea(i)
                    maxContour = i
        
        (x, y, w, h) = cv2.boundingRect(maxContour)
        x0 = int(x+w/2)
        y0 = int(y+h/2)
        r = int(h/2)
        if maskS[y0][x0] != 0:
            cv2.circle(frame, (x0, y0), r, (255, 255, 255), 2)
        
        cv2.imshow("Image", frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    zaznavanjeStevca()