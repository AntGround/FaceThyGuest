from PIL import Image
import cv2
import base64
import io
import numpy as np

"""
    Conver Base64 string to numpy.ndarray so that it can processed by opencv and deepface
"""
def stringToRGB(base64_string):
    imgdata = base64.b64decode(str(base64_string))
    img = Image.open(io.BytesIO(imgdata))
    opencv_img= cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    return opencv_img 

def rgbToString(image_data):
    retval, buffer = cv2.imencode('.jpg', image_data)
    jpg_as_text = base64.b64encode(buffer)
    return "data:image/jpg;base64,"+jpg_as_text.decode("utf-8") 