import base64
import os
from app import app, socketio, db, cache
from flask import request, jsonify
from app.models import GuestModel, MembershipModel, GuestFaceImagesModel
import app.utils as utils
import app.FaceStuff as FaceStuff
import cv2
from flask_cors import cross_origin
from deepface import DeepFace
from os import listdir
from os.path import join, isfile
from collections import Counter
from app import celery
from celery.result import AsyncResult
import requests

@celery.task
def get_something(url):
    res = requests.get(url)
    count = len(res.text)
    requests.post("http://localhost:5000/task_status", json={"data":count})
    return {"data":count}

@socketio.on("image")
def get_image(imageData):

    #setup response structure
    response = {
        "imageData" : "",
        "faceData" : [],
        "task_id": "",
    }

    #convert base64 image to np.ndarray image
    image_ndarray = utils.stringToRGB(imageData)
    orig = utils.stringToRGB(imageData)
    secondary_dataset_path =  join(app.root_path, "FaceStuff", "DetectionPhase")

    image_count = max([ int(f.split("_")[0][1:]) for f in listdir(secondary_dataset_path) if isfile(join(secondary_dataset_path, f)) ], default=0)

    detection_phase_files = [ f for f in listdir(secondary_dataset_path) if isfile(join(secondary_dataset_path, f)) and f.startswith("u")]

    print(image_count)
    if (image_count % 20 == 0) and (image_count > 3):
        print("inside")
        task = FaceStuff.categorizeUnkown.delay(secondary_dataset_path)
        response['task_id'] = task.id
    # #get bounding box coordinates for all faces in the image
    faces = FaceStuff.detectFace(image_ndarray, 640, 480)

    #loop over each bounding box
    for face_count, (x, y, w, h) in enumerate(faces):

        #draw a rectangle in the image based on current bounding box cooredinates
        cv2.rectangle(image_ndarray, (x, y), ( x+w, y+h), (255,0,0), 2)

        #crop out the face from the image
        face =  image_ndarray[y:y+h, x:x+w]

        #send cropped face to face recognizer and get guest id, which you can put into guest table to get more info
        face_name = FaceStuff.recognizeFace(face, detector_backend="ssd")

        if face_name == "" or face_name.startswith("u"):
            # FaceStuff.saveUnknown(orig[y-30:y+h+30, x-30:x+w+30], write_path=app.root_path, face_name=face_name)
            # FaceStuff.saveUnknown(orig[y:y+h, x:x+w], write_path=app.root_path, face_name=face_name)
            file_name = f"u{image_count+1}_{face_count+1}.jpg"
            FaceStuff.saveImage(orig[y:y+h, x:x+w], secondary_dataset_path, file_name=file_name)
        else:
            file_name = f"k{image_count+1}_{face_count+1}_{face_name}.jpg"
            FaceStuff.saveImage(orig[y:y+h, x:x+w], secondary_dataset_path, file_name=file_name)
        #since using making db calls for every guest id is expensive, we use a cached version of the db to get guest info
        face_data = cache.get(face_name)

        color =(0,0,0)

        if face_name == "":
            color =(0,0,255)
        else:
            color = (255,0,0)        
        #draw a rectangle in the image based on current bounding box cooredinates
        cv2.rectangle(image_ndarray, (x, y), ( x+w, y+h), color, 2)
        
        face_data = face_data or "Unknown"
        
      
        
        #write guest info json string on the image below wherever the current bounding box is at
        cv2.putText(
            image_ndarray,
            str(face_data),
            (x+5, y+h-5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2
        )
        
        

        #package up all the details we've gathered so far to send to frontend
        response["faceData"].append({
            "face":(str(x), str(y), str(w), str(h)),
            "faceB64":utils.rgbToString(face),
            "name":face_name
        })
    #convert the the processed np.ndarray image back to base64 image to be displayed on frontend
    response["imageData"] = utils.rgbToString(image_ndarray)

    #emit an event containing response data
    socketio.emit("response_back", response)


# @app.route('/task_status/<task_id>', methods=['GET'])
# def get_task_status(task_id):
#     task = AsyncResult(task_id, backend=app.config['result_backend'])
#     print("lllllllllllllllllllllllllllllll", task.ready)
#     print("lOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n", task.info)
#     return {
#         'status': task.status,
#         'info': str(task.info),
#     }

@app.route("/get_images", methods=['POST'])
def get_images():
    dataset_dir = app.config['secondary_dataset_path']
    ufiles = request.json['udata']
    kfiles = request.json['kdata'] if 'kdata' in request.json else []
    response = { 'udata':{}, 'kdata':{} }
    for ufile in ufiles:
        path_to_ufile = join(dataset_dir, ufile)
        with open(path_to_ufile, "rb") as file:
            image_base64 = base64.b64encode(file.read())
            response['udata'][ufile]=image_base64.decode("utf-8")
    return response

@app.route('/clear_detection_dir', methods=['GET'])
def clear_detection_dir():
    try:
        dataset_dir = app.config['secondary_dataset_path']
        for file in listdir(dataset_dir):
            file_path = join(dataset_dir, file)
            os.remove(file_path)
        return {'status':'yes'}
    except Exception as e:
        print(e)
        return {'status':'no'}

@app.route('/task_status', methods=['POST'])
def get_task_status():
    socketio.emit("task_done", request.json)
    return ""

@app.route('/guest', methods=['POST','GET'])
def add_guest():

    if request.method == 'POST':
        # create a new guest 
        new_guest= GuestModel(request.json["guest_name"],request.json["room_number"],request.json["id_card"],request.json["profile_url"],request.json["membership_id"])

        #commit to db
        db.session.add(new_guest)
        db.session.commit()

        #get membership details for the guest
        membership = MembershipModel.query.get(new_guest.membership_id)

        #update cache with newly added guest
        cache.set(str(new_guest.id), {"guest_name":new_guest.guest_name, "room_number":new_guest.room_number, "membership":membership.membership_name})
        
        faces = request.json['faces']
        name = request.json['guest_name']
        documents = request.json['documents']

        # save the updloaded faces for recongnition in dataset       
        for i, face in enumerate(faces):
            face_cv = utils.stringToRGB(face)
            filename = os.path.join(app.root_path, "FaceStuff", "dataset", f"{new_guest.id}_{i}.jpg")
            cv2.imwrite(filename, face_cv)
            try: # delete old representation file since we're adding new images
                os.remove(os.path.join(app.root_path, "FaceStuff", "dataset", "representations_facenet.pkl"))
                os.remove(os.path.join(app.root_path, "FaceStuff", "dataset", "representations_sface.pkl"))
            except OSError as e:
                print(e)
                pass
        for i, document in enumerate(documents):
            document_cv = utils.stringToRGB(document)
            filename = os.path.join(app.root_path, "Documents", f"{new_guest.id}_{i}.jpg")
            cv2.imwrite(filename, document_cv)
        return {'data':[ "Guest Added Successfully" ]}

    elif request.method == 'GET':
        return {'data': [store.json() for store in GuestModel.query.all()]}

@app.route('/guest/<guest_id>', methods=['GET'])
def get_guest(guest_id):
    if request.method == 'GET':
        guest = db.session.query(GuestModel.guest_name, GuestModel.room_number, MembershipModel.membership_name)\
            .join(GuestModel, MembershipModel.id==GuestModel.membership_id)\
            .filter(GuestModel.id==guest_id).first()     
        print(cache.get(str(guest_id)))
        return {'data': [ guest._asdict() ]}

@app.route('/guest_face_image', methods=['POST'])
def add_guest_face_image():
    if request.method == 'POST':
        new_guest_face_image= GuestFaceImagesModel(request.json["guest_id"],request.json["face_images"])
        db.session.add(new_guest_face_image)
        db.session.commit()
        return {'data':[ "New Guest Face Image Added Successfully" ]}


@app.route('/membership', methods=['GET'])
def get_membership():
    if request.method == 'GET':
        return {'data': [store.json() for store in MembershipModel.query.all()]}

@app.route('/verify', methods=['POST'])
def verify_two_face():
    face1_b64 = request.json['face1']
    face2_b64 = request.json['face2']
    face1_ndarray = utils.stringToRGB(face1_b64)
    face2_ndarray = utils.stringToRGB(face2_b64)
    
    model_response = DeepFace.verify(face1_ndarray, face2_ndarray, model_name="Facenet")

    return model_response

@app.route('/textextract', methods=['POST'])
def get_text_from_document():
    document_b64 = request.json['document']
    document_ndarray = utils.stringToRGB(document_b64)
    res = FaceStuff.get_text(document_ndarray)
    return {"data": res} 