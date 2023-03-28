import cv2 as cv

image = cv.imread('dir2023.jpg')
hsv = cv.cvtColor(image, cv.COLOR_RGB2HSV)
gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
cv.imshow('image', image)
cv.imshow('HSV', hsv)
cv.imshow('gray', gray)
cv.waitKey(0)