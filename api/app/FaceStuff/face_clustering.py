import pickle
from os import listdir
from os.path import join, isfile
from deepface import DeepFace
import numpy as np
from sklearn.cluster import DBSCAN
import math
import base64
import requests
from app import celery

def getEmbeddings(file):
    return DeepFace.represent(
        img_path = file,
        model_name = "SFace",
        align=False,
        normalization=False,
        enforce_detection=False
    )

def getFaceDataFromImages(path):
    image_files = [ f for f in listdir(path) if isfile(join(path, f)) and f.endswith(".jpg") and f.startswith("u")]
    print("images found")
    face_data = []
    for image in image_files:
        image_path = join(path, image)
        embeddings = getEmbeddings(image_path)
        if not embeddings:
            continue
        else:
            face_data.append([ image, embeddings])

    # raw_face_data = [ [image, getEmbeddings(join(path, image))] for image in image_files ]
    # with open(join(path, "faceData.dat"), "wb") as file:
    #     pickle.dump(face_data, file)
    return face_data

@celery.task
def categorizeUnkown(path, force_new_embeddings = False):
    face_data = []
    face_data = getFaceDataFromImages(path)
    known_face = [ f for f in listdir(path) if isfile(join(path, f)) and f.endswith(".jpg") and f.startswith("k")]

    encodings = [x[1] for x in face_data]

    clt = DBSCAN(metric="euclidean", eps=2.5)
    clt.fit(encodings)
    
    print(clt.labels_)
    labelIDs = np.unique(clt.labels_)
    numUniqueFaces = len(np.where(labelIDs > -1)[0])
    print("[INFO] # unique faces: {}".format(numUniqueFaces))

    data = list(zip([ x[0] for x in face_data], map(int, clt.labels_)))
    print(data)
    data = [ x for x in data if x[1] != -1]
    labeled_face_data = {}
    for ele in data:
        image_file = ele[0]
        image_data = ""
        image_label = ele[1]
        with open(join(path, image_file), "rb") as file:
            image_b64 = base64.b64encode(file.read())
            image_data = "data:image/png;base64,"+ image_b64.decode("utf-8")
        if image_label in labeled_face_data:
            labeled_face_data[image_label].append(image_data)
        else:
            labeled_face_data[image_label] = [image_data]
    requests.post("http://localhost:5000/task_status", json={"udata":labeled_face_data, "kdata":known_face})
    return "lol"

def get_distance(data):
    final = []
    for x1, y1 in data:
        x1 = x1.split(".")[0][1:]
        for x2, y2 in data:
            x2 = x2.split(".")[0][1:]
            distance = math.dist(y1, y2)
            final.append((x1, x2, distance))
    return final

# ret = categorizeUnkown("DetectionPhase", force_new_embeddings=False)