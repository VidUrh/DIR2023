'''
This script is used to calibrate the origin of the camera.
It is used to find the coordinates of the origin of the camera in the robot frame.
'''
import cv2
import time
import json
import math

NUM_SQUARES = 14
CALIBRATION_SQUARE_WIDTH = 15
CALIBRATION_SQUARE_HEIGHT = 10
CALIBRATION_SQUARE_SIZE_MM = 25  # mm


def dist(p1):
    return ((p1[0]**2+p1[1])**2)**0.5


def detectCheckerBoard(image, grayImage, criteria, boardDimension):
    ret, corners = cv2.findChessboardCorners(grayImage, boardDimension)
    print(ret)
    if ret == True:
        corners1 = cv2.cornerSubPix(
            grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv2.drawChessboardCorners(image, boardDimension, corners1, ret)

        if dist(corners1[0][0]) > dist(corners1[-1][0]):
            corners = list(reversed(corners1))

        # Get coordinates of corners
        # Top left corner
        xTopL = corners[0][0][0]
        yTopL = corners[0][0][1]
        cv2.putText(image, "TopLeft", (int(xTopL), int(yTopL)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Print "TopLeft" near the circle
        cv2.circle(image, (int(xTopL), int(yTopL)), 7,
                   (0, 0, 255), 2)  # Draw a circle on the corner

        # Top right corner
        xTopR = corners[NUM_SQUARES][0][0]
        yTopR = corners[NUM_SQUARES][0][1]
        cv2.putText(image, "TopRight", (int(xTopR), int(yTopR)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)  # Print "TopRight" near the circle
        cv2.circle(image, (int(xTopR), int(yTopR)), 7,
                   (0, 255, 255), 2)  # Draw a circle on the corner


        originRotation = math.atan((yTopR - yTopL) / (xTopR - xTopL))
        PIXEL_TO_MM = (NUM_SQUARES * CALIBRATION_SQUARE_SIZE_MM)/(math.sqrt((yTopR -
                                    yTopL) ** 2 + (xTopL-xTopR)**2))
        with open("originPoints.json", "w") as f:
            json.dump({
                "origin": [int(xTopL), int(yTopL)],
                "x": [int(xTopR), int(yTopR)],
                "pixelToMm": PIXEL_TO_MM,
                "originRotation": originRotation
            }, f)

    return image, ret

import pickle

#ret, frame = True, cv2.imread("sahovnica.jpg")
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

with open("calibration.pkl", 'rb') as calibrationFile:
    data = pickle.load(calibrationFile)
    cameraMatrix = data['cameraMatrix']
    distV = data['dist']
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        cameraMatrix, distV, (960, 540), 1, (960, 540))
    
ret, frame = cap.read()
frame = cv2.undistort(frame, newcameramtx, distV, None, newcameramtx)
frame= cv2.resize(frame, (0, 0), fx=0.9, fy=0.9)
frame = frame[20:380, 50:580]

CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

gray = cv2.equalizeHist(gray)

image, board_detected = detectCheckerBoard(
    frame, gray, CRITERIA, (CALIBRATION_SQUARE_WIDTH, CALIBRATION_SQUARE_HEIGHT))

cv2.imshow("test1", image)
cv2.waitKey(0)
