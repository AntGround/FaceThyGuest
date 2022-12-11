import { useEffect, useRef, useState } from "react";
import { Button, Modal, Ratio } from "react-bootstrap";
import ReactCrop from 'react-image-crop'
import 'react-image-crop/dist/ReactCrop.css'


export default function UploadDocument(props){

        const videoRef = useRef(null);
        const imgRef = useRef(null);
        const [show, setShow] = useState(false);
        const [stream, setStream] = useState(null);
        const [screenshotB64, setScreenshotB64] = useState(null);
        const [crop, setCrop] = useState();
        const imgRef2 = useRef(null);
        useEffect(()=>{

            console.log("effect")

            if(show && (!stream)){
                navigator.mediaDevices
                    .getUserMedia({video:true})
                    .then( stream => {
                        videoRef.current.srcObject = stream;
                        setStream(stream);
                    })
                    .catch( e => {
                        console.log("Shit Happend");
                        console.log(e);
                    })
                }

        return () => {
            console.log("effect cleanup")
            console.log(stream);
            if(stream)
            {
                console.log("clean stream")
                stream.getTracks().forEach(track => track.stop())
                setStream(null);
            }
        }

    }, [show, stream])

    const handleClose = () => {
        setScreenshotB64(null);
        setCrop(null);
        setShow(false);
    }
    const handleSave = () => {
        const document = cropElement(imgRef.current, crop.x, crop.y, crop.width, crop.height);
        setScreenshotB64(null);
        setCrop(null);
        setShow(false);
        props.handleDocumentUpload(document);

    }
    const handleScreenshot = () => {
        const image_b64 = cropElement(videoRef.current);
        console.log(crop)
        setScreenshotB64(image_b64);
    
    }





    console.log("render")
    return(
        <div>
            <a style={{cursor: "pointer", textDecoration:"none", color:"black"}} onClick={()=>setShow(true)}>
                <div className="card" style={{width: "100%", height: "80%"  }}>
                    <div className="card-body m-5 p-5 text-center">
                        <img src="/scan.png" className="img-fluid rounded-start mt-5" ref={imgRef2} style={{width:"12%"}} alt="..."/>
                        <h5 className="card-title text-center my-4">Click to Scan Documents</h5>
                    </div>
                </div>
            </a>
            

            <Modal size="lg" show={show} onHide={() => setShow(false)} animation={false}>
                <Modal.Header closeButton>
                <Modal.Title>Upload ID Card</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {/* <Ratio aspectRatio={"4x3"}> */}
                        <>
                            { (show && !screenshotB64) && <video id='video' autoPlay ref={videoRef}/>}
                            { screenshotB64 && 
                                <div>
                                    <ReactCrop crop={crop} onChange={ c => setCrop(c)}>
                                        <img ref={imgRef} src={screenshotB64} alt="lol"/>
                                    </ReactCrop>
                                    
                                </div>}
                        </>
                    {/* </Ratio> */}
                </Modal.Body>
                

                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Close
                    </Button>
                    <Button variant="secondary" onClick={() => {}}>
                        Local Upload
                    </Button>
                    <Button variant="secondary" onClick={handleScreenshot}>
                        Take Photo 
                    </Button>
                    <Button variant="primary" onClick={handleSave}>
                        Save Changes
                    </Button>
                </Modal.Footer> 
            </Modal>
        </div>
    );
}




const cropElement = (ele, x=0, y=0, width=640, height=480) => {
    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(ele, x, y,  width, height, 0, 0, width, height);
    var dataURI = canvas.toDataURL('image/jpeg'); // can also use 'image/png'
    return dataURI
}



