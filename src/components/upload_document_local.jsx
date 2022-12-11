import axios from "axios";
import { useRef, useState } from "react";
import { Button, Modal } from "react-bootstrap";
import ReactCrop from 'react-image-crop'
import 'react-image-crop/dist/ReactCrop.css'


export default function UploadDocumentLocal(props){
    const [show, setShow] = useState(false);
    const [fileData, setFileData] = useState(null);
    const [crop, setCrop] = useState();
    const [startImage, setStartImage] = useState(null);
    const [imageTextData, setImageTextData] = useState({});

    const imgRef = useRef();

    const handleChange = (e) => {
        
        let reader = new FileReader();
        let file = e.target.files[0];
        setCrop(null);
        reader.onloadend = () => {
            setStartImage(reader.result);
            setFileData(reader.result);
        }

        reader.readAsDataURL(file)
    }

    const checkFace = (e) => {
        if(!props.profileSet)
        {
            alert("Set a PP first");
            return;
        }
        const face1 = props.profilePicture.split(",")[1]
        const face2 = fileData.split(",")[1]
        axios.post("http://localhost:5000/verify", { face1:face1, face2:face2 })
            .then(({data}) => alert(`Same Face : ${data.verified}`))
            .catch(res => console.log(res))

    }
    const cropIt = () => {
        const image = new Image()
        image.src = fileData
        const cropped_image = cropElement(image, crop.x, crop.y, crop.width, crop.height)
        setFileData(cropped_image)
        setCrop(null)
    }

    const reset = () => {
        setCrop(null)
        setFileData(startImage)
        setImageTextData({})
    }
    
    const get_text = () => {
        const document = fileData.split(",")[1]
        axios.post("http://localhost:5000/textextract", { document:document})
            .then(({data}) => {
                console.log(data)
                const res = parseText(data.data)
                setImageTextData(res);
                
            })
            .catch(res => console.log(res))
    }

    const submit = () => {
        setCrop(null)
        setFileData(null)
        setStartImage(null)
        setShow(false)
        props.handleDocumentUpload(fileData, imageTextData)
    }
    return(
        <div>
        
            <a style={{cursor: "pointer", textDecoration:"none", color:"black"}} onClick={()=>setShow(true)}>
                <div className="card" style={{width: "100%", height: "80%"  }}>
                    <div className="card-body m-5 p-5 text-center">
                        <img src="/scan.png" className="img-fluid rounded-start mt-5" style={{width:"12%"}} alt="..."/>
                        <h5 className="card-title text-center my-4">Click To Upload From Local </h5>
                    </div>
                </div>
            </a>
            

            <Modal size="lg" show={show} onHide={() => setShow(false)} animation={false}>
                <Modal.Header closeButton>
                <Modal.Title>Upload ID Card (Local)</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div class="mb-3">
                        <label class="form-label">Default file input example</label>
                        <input class="form-control" type="file" id="formFile" onChange={handleChange}/>
                    </div>
                    <div className=''>
                        {
                            fileData &&
                            <ReactCrop crop={crop} onChange={ (c, pc) => setCrop(pc) }>
                                <img alt="alt" src={fileData} ref={imgRef} className="img-fluid"/>
                            </ReactCrop>
                        }
                        <div>
                            <ul>
                                { Object.keys(imageTextData).map( key => <li> {key} = {imageTextData[key]}</li>)}
                            </ul>                            
                        </div>
                    </div>

                </Modal.Body>
                

                <Modal.Footer>
                    <Button variant="secondary" onClick={reset}>
                        Reset
                    </Button>
                    <Button variant="secondary" onClick={cropIt}>
                        Crop
                    </Button>
                    <Button variant="secondary" onClick={checkFace} disabled={!props.profileSet}>
                        Check Face
                    </Button>
                    <Button variant="secondary" onClick={get_text}>
                        Get Details
                    </Button>
                    <Button variant="secondary" onClick={submit}>
                        Submit
                    </Button>
                </Modal.Footer> 
            </Modal>
        </div>
    );
}



const parseText = (text) => {
    const res = {}
    text = text.toLowerCase();
    const split_text = text.split("\n").filter( t => t !== '');

    let incomeFlag = 0;
    if(text.includes("income")||text.includes("tax"))
        incomeFlag = true;
    if(incomeFlag)
    {
        const i = split_text.findIndex( x => /name/.test(x))
        res.name = split_text[i+1]
        return res
    } else {
        const i = split_text.findIndex( t => /^to/i.test(t))
        res.name = split_text[i+2]
        return res
    }
}

const cropElement = (ele, x, y, width, height) => {
    const naturalWidth = ele.naturalWidth/100
    const naturalHeight = ele.naturalHeight/100
    x = x*naturalWidth
    y = y*naturalHeight
    width = width*naturalWidth
    height = height*naturalHeight

    console.log(x, y, width, height)
    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(ele, x, y,  width, height, 0, 0, width, height);
    var dataURI = canvas.toDataURL('image/png'); // can also use 'image/png'
    return dataURI
}



