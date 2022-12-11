import { useEffect, useRef } from "react";

export default function Video(props){
    const videoRef = useRef(null);
    useEffect(()=>{
        videoRef.current.srcObject = props.srcObject;
    }, [props.srcObject]);
    return (
        <video  autoPlay ref={videoRef}></video>
    );
}