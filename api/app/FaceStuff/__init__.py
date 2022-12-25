from deepface import DeepFace
from deepface.commons.functions import preprocess_face
import cv2
import numpy as np
import os
from os import listdir
from os.path import join, isfile
import ftfy
import pytesseract
import pickle
from app.FaceStuff.face_clustering import categorizeUnkown
from filelock import FileLock

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

def recognizeFace(face:np.ndarray or str, detector_backend="opencv"):
    dataset_dir = os.path.join(package_directory, "dataset")
    recognition_result = DeepFace.find(face, db_path=dataset_dir, enforce_detection=False, model_name=model_name, detector_backend=detector_backend, silent=True, prog_bar=True)
    face_name_paths = list(map(os.path.basename, recognition_result.identity.to_list()))
    face_names = list(map(removeShit, face_name_paths))

    if(len(face_names)>0):
        face_id = max(set(face_names), key=face_names.count)
        return face_id
    else:
        return ""

def saveImage(face:np.ndarray, path:str, file_name):
    cv2.imwrite(join(path, file_name), face)

def saveUnknown(face:np.ndarray, write_path, face_name):
    dataset_dir = os.path.join(package_directory, "DetectionPhase")
    uface_file_ids = [ f.split(".")[0][1:] for f in listdir(dataset_dir) if isfile(join(dataset_dir, f)) and f.startswith("u") ]

    next_face_id = 0
    next_face_count = 0
    if uface_file_ids:
        if face_name == "":
            next_face_id = max(map(int, [x.split("_")[0] for x in uface_file_ids]), default=0) + 1
        else:
            next_face_id = int(face_name[1:])

        next_face_count = max(map(int, [x.split("_")[1] for x in uface_file_ids if x.startswith(str(next_face_id))]), default=0) + 1

        if next_face_count > 10:
            return
    filename = os.path.join(write_path, "FaceStuff", "DetectionPhase", f"u{next_face_id}_{next_face_count}.jpg")

    # if next_face_id > 64 :
    #     return 1

    # representation = DeepFace.represent(face
	# 					, model_name = model_name, model = recognition_model
	# 					, enforce_detection = "True", detector_backend = "opencv"
	# 					, align = "True"
	# 					, normalization = "base"
	# 					)

    # writeToRepresentaion([filename, representation], path=os.path.join(write_path, "FaceStuff", "dataset", "representations_facenet.pkl"))
    cv2.imwrite(filename, face)
    # os.remove(os.path.join(write_path, "FaceStuff", "dataset", "representations_facenet.pkl"))

def writeToRepresentaion(data, path):
    objects = []
    with (open(path, "rb")) as openfile:
        while True:
            try:
                objects.append(pickle.load(openfile))
            except EOFError:
                break
    objects[0].append(data)
    print(len(objects[0]))
    
    with open(path, "wb") as file:
        pickle.dump(objects[0], file)

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

