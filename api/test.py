import cv2
import pytesseract
import numpy as np


img = cv2.imread("pan.jpg")
new_image = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
kernel = np.ones((1,1), np.uint8)
img = cv2.dilate(img, kernel, iterations=1)
img = cv2.erode(img, kernel, iterations=1)
img = cv2.GaussianBlur(img, (5,5), 0)
img = cv2.medianBlur(img,5)
img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
# img = deskew(img)

while True:


    cv2.imshow("Dist Otsu", img)   
    # cv2.imshow('camera',thresh) 
    # cv2.imshow('camera',gray) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    
print(pytesseract.image_to_string(img))