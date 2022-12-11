import axios from "axios";
import { useFormik } from "formik";
import { defineDriver, keys } from "localforage";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import UploadDocument from "../components/upload_document";
import { Button, Form, Modal } from "react-bootstrap";
import UploadDocumentLocal from "../components/upload_document_local";

export default function FaceRegistraionPage(){
    const location = useLocation();
    const [allFaceData, setAllFaceData] = useState([]) // <array> { imageData : <string>, faceData:<array> { face:<array> bounding box, faceB64:<string>, name:<string>}}
    const [whoThat, setWhoThat] = useState([])  // { faceB64:<string>, selected:<bool>}
    const [membership, setMembership] = useState([]) // [{id:<int>, name:<string>}]
    const [profileUrl, setProfileUrl] = useState("profile.png")
    const [profileFlag, setProfileFlag] = useState(false)
    const [documents, setDocuments] = useState([]);
    const formik = useFormik({
      initialValues: {
        guest_name: "",
        id_card: "",
        room_number: "",
        membership_id: -1,
        preference: "",
        upload_mode:"webcam",
      },
      onSubmit: (data) => {

        const face64sSelectedObjs = whoThat.filter( face => face.selected ) 
        const faceB64s = face64sSelectedObjs.map( face => face.faceB64.split(",")[1]+"=")
        const processed_documents = documents.map( b64 => b64.split(",")[1])
        if(faceB64s.length === 0)
        {
            prompt("Are you an idiot ?");
            return;
        }
        const req = { ...data, faces:faceB64s, profile_url:profileUrl , documents:processed_documents}
        axios.post("http://localhost:5000/guest", req)
            .then(resp=>{
                console.log(resp)
            })
            .catch(resp=>{
                alert("failed")
            })
      },
    });
    useEffect(()=>{
        
        axios.get("http://localhost:5000/membership")
            .then(resp => {
                setMembership(resp.data.data)
            })

        const imageDataRaw = location.state;
        const imageData = processData(imageDataRaw)
        console.log(imageData)
        let count = -1000;
        const allfacedata = []
        const unkownfacedata = []
        imageData.forEach(ele => {
            const parentImage = ele.imageData;
            const localList = []
            if(ele.faceData.length > 0){
                ele.faceData.forEach( face => {
                    if(face.name ==="" && count < 5){
                        localList.push(face);
                        unkownfacedata.push({faceB64:face.faceB64, selected:false});
                        count+=1;
                    }
                });
            };
            allfacedata.push({parent:parentImage, localList:localList})
        });
        // console.log(allfacedata); 
        setAllFaceData(allfacedata);
        unkownfacedata.splice(0,15);
        setWhoThat(unkownfacedata)

    }, []);

    const handleClick = (id) => {
        const previous = JSON.parse(JSON.stringify(whoThat))
        previous[id].selected = !previous[id].selected
        if(!profileFlag){
            setProfileUrl(previous[id].faceB64);
            setProfileFlag(true);
        }
        setWhoThat(previous)
    }

    const handleDocumentUpload = (image_b64, formFillData) => {
        console.log(image_b64, formFillData)
        const current_documents = [...documents];
        current_documents.push(image_b64);
        setDocuments(current_documents);
        const guest_name = formFillData.name || formik.values.guest_name
        formik.setFieldValue("guest_name", guest_name)
    }
    let imgComponents;
    if(false){
        imgComponents = allFaceData.map( (ele, i) => 
            <div key={i} className='row'>
                <div className='col'>
                <img src={ele.parent} alt="shit"/>

                </div>
                <div className="col">
                    {
                        ele.localList.map( (face,j) => 
                        <div key={j}>
                            <img src={face.faceB64} alt='lol'/>
                            <p>{JSON.stringify(face?.guess)}</p>
                            <p>{JSON.stringify(face?.faceProb)}</p>
                        </div>)
                    }
                </div>
            </div>)

    }
    else{
        imgComponents = whoThat.map( (ele, i) =>
            <div key={i}>
                <img src={ele.faceB64} alt='shit' onClick={() => handleClick(i)} width={100} height={100} className={ ele.selected ? "border border-5 border-danger m-1":" m-1"}/>
            </div>
        )
    }
    const membershipOptionComponents = membership.map( data => <option value={data.id} key={data.id}>{data.name}</option>)
    return(
    <div className="container-fluid">
        <div className="container">
            <h1 className="display-1">Guest Registraction</h1>
            <hr/>
            <div className="row mb-3">
                <div className="col">
                    <form onSubmit={formik.handleSubmit} className="mb-3">
                        <div className="mb-3 rounded-circle">
                            <img src={profileUrl} alt="profile url" width={100} height={100}/>
                        </div>
                        <div className="input-group mb-3">
                            <span className="input-group-text" id="basic-addon1">Name</span>
                            <input type="text" className="form-control" name="guest_name" value={formik.values.guest_name} onChange={formik.handleChange} placeholder="Name" aria-label="Name" aria-describedby="basic-addon1"/>
                        </div>
                        <div className="input-group mb-3">
                            <select className="form-select" aria-label="Default select example" name="membership_id" value={formik.values.membership_id} onChange={formik.handleChange}>
                                {membershipOptionComponents}
                                <option value='-1'>No Club</option>
                            </select>
                        </div>
                        <div className="input-group mb-3">
                            <span className="input-group-text" id="basic-addon1">ID Number</span>
                            <input type="text" className="form-control" name="id_card" value={formik.values.id_card} onChange={formik.handleChange} placeholder="ID" aria-label="ID" aria-describedby="basic-addon1"/>
                        </div>
                        <div className="input-group mb-3">
                            <span className="input-group-text" id="basic-addon1">Room Number</span>
                            <input type="text" className="form-control" name="room_number" value={formik.values.room_number} onChange={formik.handleChange} placeholder="Room Number" aria-label="Room Number" aria-describedby="basic-addon1"/>
                        </div>
                        <div className="input-group mb-3">
                            <span className="input-group-text" id="basic-addon1">Preferences</span>
                            <input type="text" className="form-control" name="preference" value={formik.values.preference} onChange={formik.handleChange} placeholder="Preferences" aria-label="Preferences" aria-describedby="basic-addon1"/>
                        </div>
                        
                    </form>
                </div>
                <div className="col">
                    {formik.values.upload_mode === "webcam" && <UploadDocument handleDocumentUpload={handleDocumentUpload}/>}
                    {formik.values.upload_mode === "local" && <UploadDocumentLocal profileSet={profileFlag} profilePicture={profileUrl} handleDocumentUpload={handleDocumentUpload}/>}
                </div>
            </div>
            <div className="row">
                <div className="col">
                </div>
                <div className="col">
                    <select class="form-select" name="upload_mode" onChange={formik.handleChange} value={formik.values.upload_mode} aria-label="Default select example">
                        <option selected>Open this select menu</option>
                        <option value="webcam">Webcam</option>
                        <option value="local">Local</option>
                    </select>
                </div>
            </div>

            <div className="mb-3">
                <h1 className="display-5">Uploaded Documents</h1>
                <div className="d-flex flex-row flex-wrap p-4 border rounded-3 border-1 border-secondary">
                    {
                       documents.map( (d,i) => <img src={d} key={i} alt="document" className="p-1 img-fluid rounded rounded-4" width="400"/>) 
                       
                    }
                </div>
            </div>
            <div className="mb-3">
                <h1 className="display-5">Face Tranining set</h1>
                <div className="d-flex flex-row flex-wrap p-4 border rounded-3 border-1 border-secondary">
                    {imgComponents}
                </div>

            
            </div>
            <Button type='submit' variant="success">Submit</Button>
        </div>
    </div>)
}

const rectangleOverlap2 = (rect1, rect2) => {
    // console.log(rect1)
    rect1 = rect1.map((x) => parseInt(x, 10))
    rect2 = rect2.map((x) => parseInt(x, 10))
    // console.log(rect1)

    const A = { x1: rect1[0], x2:rect1[2]+rect1[0], y1:rect1[1], y2:rect1[1]-rect1[3]};
    const B = { x1: rect2[0], x2:rect2[2]+rect2[0], y1:rect2[1], y2:rect2[1]-rect2[3]};
  
    const ca = B.x1 <= A.x2 
    const cb = B.y1 >= A.y2
    const cc = B.x2 >= A.x1
    const cd = B.y2 <= A.y1
    const ca2 = B.x2 <= A.x2
    const cb2 = B.y2 <= A.y2
    if(ca && cb && cc && cd && ca2 && cb2)
    {
        return 1
    }
    if(!ca || !cb || !cc || !cc)
    {
        return 0
    }
  
    const SA = (A.x2-A.x1)*(A.y1-A.y2)
    const SB = (B.x2-B.x1)*(B.y1-B.y2)
    const SI = Math.max(0, Math.abs(Math.min(A.x2, B.x2) - Math.max(A.x1, B.x1))) * Math.max(0, Math.abs(Math.max(A.y2, B.y2) - Math.min(A.y1, B.y1)))
    const SU = SA + SB - SI
    const overlap_percent = parseFloat(SI)/parseFloat(SU)
    return overlap_percent
  }
  
  const processData = (imageHistory) => {
    imageHistory.forEach( (image, image_i) => { //loop images

        if(image_i<10) return;
        // console.log("\t", image_i)
        image.faceData.forEach( (faceRef, face_i) => { //loop faces
            // console.log("\t\t", face_i)
            
            const faceProbList = []

            if(faceRef.name === ""){  // start checking validity of invalid face

                for(let check_i=image_i; check_i>(image_i-5);check_i--){    // start loop over last five images 
                    const current_image = imageHistory[check_i];
                    const faceProb = {}
                    current_image.faceData.forEach(faceCheck => {   // check samilarity of unkown face with known face
                        
                        if(faceCheck.name !== ""){
                            if (!(faceCheck.name in faceProb)) faceProb[faceCheck.name] = {}
                            faceProb[faceCheck.name] = {}
                            faceProb[faceCheck.name]['rects'] = [faceCheck.face, faceRef.face]
                            faceProb[faceCheck.name]['overlap'] = rectangleOverlap2(faceCheck.face, faceRef.face);
                            faceProb[faceCheck.name]['loss'] = 1/parseFloat(2^(check_i-image_i))
                            faceProb[faceCheck.name]['prob'] = rectangleOverlap2(faceCheck.face, faceRef.face) * (1/parseFloat(2^(Math.abs(image_i-check_i))))
                        }
                    });
                    faceProbList.push(faceProb)

                }
            }
            // console.log(faceProbList)
            let result = {}
            faceProbList.forEach( (item, i) => {
                let keys = Object.keys(item)
                keys.forEach( face_key => {
                    if (!(face_key in result)) result[face_key] = 0
                    result[face_key] = result[face_key] + (item[face_key].overlap/(i+1))
                })
            })
            // console.log(result)
            imageHistory[image_i].faceData[face_i].faceProb = faceProbList
            imageHistory[image_i].faceData[face_i].guess = result
            if(faceRef.name === "" && Object.keys(result)>0)
            {
                imageHistory[image_i].faceData[face_i].name =Object.keys(result).reduce((a, b) => result[a] > result[b] ? a : b);
            }


            // console.log("\t\t",imageHistory[image_i][face_i])
        })
    })
    return imageHistory
  }