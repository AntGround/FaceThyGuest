import pytesseract


image_path:str = "Capture.jpg"

pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR'
print(pytesseract.image_to_string(image_path))

# print(reader.readtext(image_path))



