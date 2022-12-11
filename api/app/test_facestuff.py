import cv2
font = cv2.FONT_HERSHEY_SIMPLEX
import FaceStuff



cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

while True:
    ret, image_ndarray =cam.read()

    faces = FaceStuff.detectFace(image_ndarray, 640, 480)
    for (x, y, w, h) in faces:
        cv2.rectangle(image_ndarray, (x, y), ( x+w, y+h), (255,0,0), 2)
        face_name = FaceStuff.recognizeFace(image_ndarray[y:y+h, x:x+w], detector_backend="ssd")
        cv2.putText(
            image_ndarray,
            face_name,
            (x+5, y+h-5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2
        )
        # resp = str(resp.identity.to_list())
        # cv2.imwrite("test.jpg", img)
        # cv2.putText(
        #             img, 
        #             resp, 
        #             (x+5,y+h-5), 
        #             font, 
        #             0.5, 
        #             (255,0,0), 
        #             2
        #            )

    cv2.imshow('camera',image_ndarray) 
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break