from deepface import DeepFace
from deepface.commons.functions import preprocess_face
import cv2
import numpy as np
import os
import ftfy
import pytesseract

package_directory = os.path.dirname(os.path.abspath(__file__))

model_name = 'Facenet'
detection_model = cv2.CascadeClassifier(os.path.join(package_directory, "haar.xml"))
recognition_model = DeepFace.build_model(model_name=model_name)

def detectFace(image:np.ndarray, width:int, height:int):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    minW = 0.1*width
    minH = 0.1*height
    bbox = []

    faces = detection_model.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )
    
    for (x, y, w, h) in faces:
        bbox.append((
            x-30,
            y-30,
            w+30,
            h+30
        ))
    return bbox

def recognizeFace(face:np.ndarray, detector_backend="opencv"):
    dataset_dir = os.path.join(package_directory, "dataset")
    recognition_result = DeepFace.find(face, db_path=dataset_dir, enforce_detection=False,model_name=model_name, detector_backend=detector_backend, silent=True, prog_bar=False)
    face_name_paths = list(map(os.path.basename, recognition_result.identity.to_list()))
    face_names = list(map(removeShit, face_name_paths))
    if(len(face_names)>0):
        return str(face_names[0])
    else:
        return ""

def get_text(img):
    cv2.resize(img, (0,0), fx=0.5, fy=0.5)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1,1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.GaussianBlur(img, (5,5), 0)
    img = cv2.medianBlur(img,5)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    res = pytesseract.image_to_string(img)
    res = ftfy.fix_text(res)
    res = ftfy.fix_encoding(res)
    # res = res.split("\n")
    # res = list(filter(lambda x: x != '', res))
    return res

def removeShit(string):
    return string.split("_")[0]
